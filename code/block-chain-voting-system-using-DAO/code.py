import cv2
import face_recognition
import os
import json
import pyttsx3
import hashlib
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk

# ---------- Voice Engine ----------
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# ---------- Blockchain ----------
class Block:
    def __init__(self, index, data, timestamp, previous_hash=''):
        self.index = index
        self.data = data
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        content = str(self.index) + str(self.data) + str(self.timestamp) + str(self.previous_hash)
        return hashlib.sha256(content.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "Genesis Block", time.time(), "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        new_block = Block(len(self.chain), data, time.time(), self.get_latest_block().hash)
        self.chain.append(new_block)

    def has_voted(self, aadhar):
        for block in self.chain[1:]:
            if block.data.get('aadhar') == aadhar:
                return True
        return False

    def get_history(self):
        return [block.data for block in self.chain[1:] if 'vote' in block.data]

voting_chain = Blockchain()

# ---------- DAO Governance ----------
DAO_FILE = "dao_proposals.json"

def load_proposals():
    if not os.path.exists(DAO_FILE):
        return []
    with open(DAO_FILE, 'r') as f:
        return json.load(f)

def save_proposals(proposals):
    with open(DAO_FILE, 'w') as f:
        json.dump(proposals, f, indent=4)

def create_proposal():
    proposer = get_valid_aadhar()
    if not proposer: return

    proposal_text = simpledialog.askstring("DAO Proposal", "Enter your proposal text:")
    if not proposal_text: return

    proposals = load_proposals()
    proposal = {
        "id": len(proposals) + 1,
        "proposer": proposer,
        "text": proposal_text,
        "votes_for": [],
        "votes_against": [],
        "status": "open"
    }
    proposals.append(proposal)
    save_proposals(proposals)
    messagebox.showinfo("Success", f"Proposal #{proposal['id']} submitted.")
    speak(f"Proposal {proposal['id']} submitted successfully.")

def vote_on_proposal():
    aadhar = get_valid_aadhar()
    if not aadhar: return

    proposals = load_proposals()
    open_proposals = [p for p in proposals if p["status"] == "open"]
    if not open_proposals:
        messagebox.showinfo("Info", "No open proposals.")
        speak("No open proposals.")
        return

    options = "\n".join([f"{p['id']}: {p['text']}" for p in open_proposals])
    selected_id = simpledialog.askinteger("Vote", f"Open Proposals:\n{options}\n\nEnter Proposal ID:")
    selected = next((p for p in open_proposals if p["id"] == selected_id), None)

    if not selected:
        messagebox.showerror("Error", "Invalid Proposal ID.")
        speak("Invalid Proposal ID.")
        return

    if aadhar in selected["votes_for"] or aadhar in selected["votes_against"]:
        messagebox.showinfo("Info", "You already voted on this proposal.")
        speak("Already voted on this proposal.")
        return

    vote = simpledialog.askstring("Your Vote", "Enter 'yes' or 'no':")
    if vote == 'yes':
        selected["votes_for"].append(aadhar)
    elif vote == 'no':
        selected["votes_against"].append(aadhar)
    else:
        messagebox.showerror("Error", "Invalid vote.")
        speak("Invalid vote.")
        return

    # Check for automatic acceptance/rejection (threshold = 3 votes)
    if len(selected["votes_for"]) >= 3:
        selected["status"] = "accepted"
    elif len(selected["votes_against"]) >= 3:
        selected["status"] = "rejected"

    save_proposals(proposals)
    messagebox.showinfo("Vote Recorded", f"Voted on Proposal #{selected['id']}")
    speak(f"Vote recorded for Proposal {selected['id']}.")

def view_proposals():
    proposals = load_proposals()
    if not proposals:
        messagebox.showinfo("Proposals", "No proposals found.")
        speak("No proposals found.")
        return
    text = ""
    for p in proposals:
        text += f"#{p['id']} - {p['text']}\n✅ {len(p['votes_for'])} ❌ {len(p['votes_against'])} | Status: {p['status']}\n\n"
    messagebox.showinfo("DAO Proposals", text)
    speak("Displaying DAO proposals.")

# ---------- Directories & Config ----------
FACE_DIR = "faces"
ENCODE_FILE = "encodings.json"
ADMIN_PASS = "admin123"

if not os.path.exists(FACE_DIR):
    os.makedirs(FACE_DIR)

# ---------- Helpers ----------
def save_encoding(name, encoding):
    encodings = {}
    if os.path.exists(ENCODE_FILE):
        with open(ENCODE_FILE, "r") as f:
            encodings = json.load(f)
    encodings[name] = encoding.tolist()
    with open(ENCODE_FILE, "w") as f:
        json.dump(encodings, f)

def load_encodings():
    encodings = {}
    if os.path.exists(ENCODE_FILE):
        with open(ENCODE_FILE, "r") as f:
            data = json.load(f)
        for name, enc in data.items():
            encodings[name] = enc
    return encodings

def delete_encoding(aadhar):
    if os.path.exists(ENCODE_FILE):
        with open(ENCODE_FILE, "r") as f:
            data = json.load(f)
        if aadhar in data:
            del data[aadhar]
            with open(ENCODE_FILE, "w") as f:
                json.dump(data, f)

def get_valid_aadhar():
    while True:
        aadhar = simpledialog.askstring("Aadhar", "Enter 12-digit Aadhar number:")
        if aadhar and len(aadhar) == 12 and aadhar.isdigit():
            return aadhar
        else:
            speak("Invalid Aadhar number.")
            messagebox.showerror("Error", "Invalid Aadhar number.")

# ---------- Core Voting Features ----------
def register_face():
    pwd = simpledialog.askstring("Admin", "Enter Admin Password:", show="*")
    if pwd != ADMIN_PASS:
        speak("Access Denied")
        messagebox.showerror("Error", "Access Denied")
        return

    aadhar = get_valid_aadhar()
    if not aadhar: return

    img_path = os.path.join(FACE_DIR, f"{aadhar}.jpg")
    if os.path.exists(img_path):
        speak("Aadhar already registered.")
        messagebox.showinfo("Info", "Aadhar already registered.")
        return

    encodings = load_encodings()
    cap = cv2.VideoCapture(0)
    speak("Look at the camera and press 'S' to capture.")
    messagebox.showinfo("Capture", "Press 'S' to capture.")

    while True:
        ret, frame = cap.read()
        cv2.imshow("Register Face", frame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            enc = face_recognition.face_encodings(rgb)
            if enc:
                for name, known_enc in encodings.items():
                    match = face_recognition.compare_faces([known_enc], enc[0])
                    if match[0]:
                        speak("Face already registered.")
                        messagebox.showerror("Error", f"Face already registered as {name}")
                        cap.release()
                        cv2.destroyAllWindows()
                        return
                save_encoding(aadhar, enc[0])
                cv2.imwrite(img_path, frame)
                speak("Face Registered Successfully.")
                messagebox.showinfo("Success", "Face Registered Successfully.")
            else:
                speak("Face not detected.")
                messagebox.showerror("Error", "Face not detected.")
            break
    cap.release()
    cv2.destroyAllWindows()

def vote():
    aadhar = get_valid_aadhar()
    if not aadhar: return

    img_path = os.path.join(FACE_DIR, f"{aadhar}.jpg")
    if not os.path.exists(img_path):
        speak("Face Image not found.")
        messagebox.showerror("Error", "Face image not found.")
        return

    encodings = load_encodings()
    known_faces = [face_recognition.face_encodings(face_recognition.load_image_file(os.path.join(FACE_DIR, f"{a}.jpg")))[0] for a in encodings]
    names = list(encodings.keys())

    cap = cv2.VideoCapture(0)
    speak("Look at the camera to cast your vote.")
    messagebox.showinfo("Info", "Look at camera. Press ESC to cancel.")
    voted_aadhar = None

    while True:
        ret, frame = cap.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_encodings(rgb)
        if faces:
            for f in faces:
                results = face_recognition.compare_faces(known_faces, f)
                if True in results:
                    i = results.index(True)
                    voted_aadhar = names[i]
                    break
        cv2.imshow("Voting", frame)
        if voted_aadhar or cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    if not voted_aadhar:
        speak("Face not recognized.")
        messagebox.showerror("Error", "Face not recognized.")
        return

    if voting_chain.has_voted(voted_aadhar):
        speak("Already voted.")
        messagebox.showinfo("Info", "You have already voted.")
        return

    choice = simpledialog.askstring("Vote", "Enter your vote (Party A/B):")
    if choice:
        voting_chain.add_block({"aadhar": voted_aadhar, "vote": choice})
        speak("Vote recorded successfully.")
        messagebox.showinfo("Success", "Vote recorded successfully.")

def view_registered():
    data = load_encodings()
    speak("Displaying registered Aadhar numbers.")
    messagebox.showinfo("Registered", "\n".join(data.keys()))

def view_history():
    history = voting_chain.get_history()
    hist_str = "\n".join([f"{b['aadhar']} ➜ {b['vote']}" for b in history])
    messagebox.showinfo("Voting History", hist_str if hist_str else "No votes recorded yet.")
    speak("Displaying voting history.")

def delete_aadhar():
    aadhar = get_valid_aadhar()
    if not aadhar: return
    if messagebox.askyesno("Confirm", f"Delete Aadhar {aadhar}?"):
        delete_encoding(aadhar)
        face_path = os.path.join(FACE_DIR, f"{aadhar}.jpg")
        if os.path.exists(face_path):
            os.remove(face_path)
        speak(f"Aadhar {aadhar} deleted.")
        messagebox.showinfo("Deleted", f"Aadhar {aadhar} deleted.")

# ---------- Modern GUI ----------
root = tk.Tk()
root.title("🗳️ Face Recognition Voting System with DAO")
root.geometry("450x550")
root.configure(bg="#f0f2f5")

style = ttk.Style()
style.theme_use("default")
style.configure("TButton",
    font=("Segoe UI", 11, "bold"),
    padding=10,
    background="#007acc",
    foreground="white",
    borderwidth=0)
style.map("TButton",
    background=[("active", "#005f99")])

title_label = tk.Label(root,
    text="🗳️ Face Voting + DAO Governance",
    font=("Segoe UI", 18, "bold"),
    fg="#222",
    bg="#f0f2f5")
title_label.pack(pady=20)

btn_frame = tk.Frame(root, bg="#f0f2f5")
btn_frame.pack(pady=10)

def create_button(text, command):
    btn = ttk.Button(btn_frame, text=text, command=command, style="TButton")
    btn.pack(pady=7, fill='x', ipadx=10)

create_button("📝 Register Face", register_face)
create_button("🗳️ Vote", vote)
create_button("📄 View Registered Users", view_registered)
create_button("📜 View Vote History", view_history)
create_button("🗑️ Delete Aadhar", delete_aadhar)
create_button("➕ Create DAO Proposal", create_proposal)
create_button("🗳️ Vote on Proposal", vote_on_proposal)
create_button("📋 View DAO Proposals", view_proposals)
create_button("❌ Exit", root.destroy)

speak("Welcome to Face Recognition Voting System with DAO Governance")
root.mainloop()
