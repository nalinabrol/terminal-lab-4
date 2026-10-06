# Start Lab 4 in your browser

Use the class Codespaces link from your instructor's email. Sign in with **your own GitHub account** and create or resume your own Lab 4 Codespace. The lab runs in its Linux terminal on Windows, Mac and Linux laptops.

## Start

1. Download your personal `Lab_4_studentNN_Access.zip` email attachment. Keep it zipped and private.
2. In the Codespace Explorer, right-click the `.uploads` folder and choose **Upload**, or drag the ZIP into that folder. Upload only your own ZIP.
3. Choose **Terminal > New Terminal**. At the repository root, run:

```bash
bash start_lab.sh
```

4. Enter your roll number when asked.
5. Open `Experiment_Book_4_Draft.md` and begin Experiment 1.

Setup installs your key outside the repository, sets private file permissions and prepares your folders on the Codespace and server. It opens a lab Bash terminal in `lab-work/lab4-YOUR-ROLL/` with SSH/SCP already configured. Your email attachment fixes your server account; your roll number only names your working folders.

Use `ssh lab-server` to connect. `exit` returns you to the Codespace; another `exit` closes the lab Bash session. To open a new session, return to the repository root and run `bash start_lab.sh` again. Saved work is kept.

After setup succeeds, you may delete the uploaded ZIP from `.uploads`. Keep the email attachment: if you rebuild or create a new Codespace and private storage is missing, upload the same ZIP again. Uploads, connection profiles and generated work are excluded from Git. Do not add your key or ZIP to a commit or share it publicly.

## Two machines

- **Codespace / local terminal:** your starting Linux machine, opened in the browser. Files here belong to the Codespace, rather than your physical laptop.
- **Lab server / server terminal:** the remote Linux machine after `ssh lab-server`.

Use `hostname`, `whoami` and `pwd` to identify where you are. All commands in the booklet use Bash, regardless of your laptop's operating system. You do not need to install Python, SSH or PowerShell tools on your laptop.

## Check your work

From your local lab folder in the lab Bash terminal, run:

```bash
check_lab
```

The checker inspects your files and the live server permissions. It leaves your files unchanged and does not submit work. Use the filenames in the booklet: `work/project.zip` or `work/project.tar.gz`, server folder `challenge-delivery`, and downloaded report `work/permissions-report.txt`.

To submit the report from your physical laptop, find it under `lab-work/lab4-YOUR-ROLL/work/` in the Codespace Explorer, right-click it and choose **Download**. Submit through your normal class submission channel.

## If something goes wrong

Check the machine you are using, your current directory and the exact error.

- **No access ZIP found:** upload your emailed access-only ZIP into `.uploads` and keep it zipped.
- **More than one ZIP / different access:** keep only your own ZIP in `.uploads`. Setup preserves installed access and refuses to replace it with another account. Ask your instructor if you uploaded the wrong one.
- **Connection lost:** reconnect and return to your server lab folder. Saved server files remain there.
- **Login or server identity error:** send the exact error to your instructor, without attaching your private key publicly. Keep host-key checking enabled.
- **Original file changed:** keep the attempt and ask your instructor for help. Setup does not restore changed files.
- **Output already exists:** inspect it and move it to an unused backup name before repeating the step. Extract archives into a new folder. Preserve the old `challenge-delivery` folder before creating a replacement.
- **Checker reports an extra line:** inspect the file before repeating an append command.

Use permission commands on your own lab files, without sudo. Stop your Codespace when finished to avoid using more compute time; keep it until you have downloaded and submitted your work.
