# Face Recognition Voting System with DAO Governance

## Overview

This project is a modern, Python-based voting system that leverages face recognition for secure voter authentication and integrates DAO (Decentralized Autonomous Organization) governance for proposal management. It features a user-friendly GUI, blockchain-backed vote recording, and voice feedback for accessibility.

---

## Features

- **Face Registration & Authentication:**
  - Register voters using their face and Aadhar number (admin protected).
  - Authenticate voters via webcam before allowing them to vote.
- **Blockchain Voting:**
  - Each vote is recorded as a block in a simple blockchain for tamper-evidence.
  - Prevents double voting using Aadhar checks.
- **DAO Governance:**
  - Any registered user can create proposals.
  - Users can vote on proposals (yes/no). Proposals are accepted/rejected based on votes.
  - View all proposals and their statuses.
- **Admin Features:**
  - View all registered users.
  - Delete a user (face and data).
- **Modern GUI:**
  - Built with Tkinter and ttk for a clean, modern look.
  - Voice feedback using `pyttsx3`.

---

## Requirements

- Python 3.7+
- [OpenCV](https://pypi.org/project/opencv-python/) (`cv2`)
- [face_recognition](https://pypi.org/project/face_recognition/)
- [pyttsx3](https://pypi.org/project/pyttsx3/)
- Tkinter (usually included with Python)

Install dependencies with:

```bash
pip install opencv-python face_recognition pyttsx3
```

---

## Usage

1. **Run the Application:**
   ```bash
   python code.py
   ```

2. **Register a Face:**
   - Click "Register Face" (admin password: `admin123`).
   - Enter a 12-digit Aadhar number.
   - Look at the camera and press 'S' to capture your face.

3. **Vote:**
   - Click "Vote".
   - Enter your Aadhar number and look at the camera.
   - If recognized and not already voted, cast your vote (Party A/B).

4. **DAO Proposals:**
   - Create a proposal or vote on open proposals.
   - Proposals are accepted/rejected after 3 yes/no votes.

5. **Other Features:**
   - View registered users, vote history, or delete a user.

---

## File Structure

- `code.py` — Main application file (GUI, blockchain, DAO, face recognition logic)
- `faces/` — Stores registered face images
- `encodings.json` — Stores face encodings for recognition
- `dao_proposals.json` — Stores DAO proposals and votes

---

## Security & Privacy
- Face data and Aadhar numbers are stored locally.
- Admin password is hardcoded as `admin123` (change in `code.py` for production).
- No data is sent to external servers.

---

## Notes
- Requires a working webcam.
- For demo/educational use. Not for real-world elections.
- Tested on Windows 10 with Python 3.9.

---

## Credits
- Face recognition: [face_recognition](https://github.com/ageitgey/face_recognition)
- GUI: Tkinter
- Blockchain logic: Custom Python implementation
- Voice: pyttsx3

---

## License
This project is for educational purposes. Please review and adapt for your own use cases. 
