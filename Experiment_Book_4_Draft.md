# Lab 4: File permissions and remote access

Draft

Name: ____________________  Roll number: __________  Section: __________

Connect to the lab server, change file permissions and transfer a project between your Codespace and the server.

**Time:** 90 minutes. Complete the account and connection setup before the session.

## Get ready

[**Open Lab 4 in GitHub Codespaces**](https://codespaces.new/nalinabrol/terminal-lab-4?quickstart=1)

You will use two Linux machines: your Codespace and the lab server. Your laptop's browser displays the Codespace terminal; the commands run in the Codespace.

- **Local terminal:** commands run in your Codespace.
- **Server terminal:** commands run on the lab server while connected through SSH.

Use `exit` to end an SSH session and return to the Codespace terminal. Your physical laptop is only used to open the browser and download your final report.

1. Open the **Lab 4 in GitHub Codespaces** link above, sign in with **your own GitHub account**, and create your own Codespace or resume your existing Lab 4 Codespace. Wait for the browser editor to load.
2. Download your personal `Lab_4_studentNN_Access.zip` from your instructor's email. Keep it zipped and private; it contains your personal SSH key.
3. In the Codespace Explorer, right-click `.uploads`, choose **Upload**, and upload only your own ZIP without extracting it.
4. Choose **Terminal > New Terminal**. At the repository root, run:

   ```bash
   bash start_lab.sh
   ```

5. Enter your roll number when asked. Begin Experiment 1 after setup opens the lab Bash terminal.

Setup prepares your Codespace and server folders, then opens the lab Bash terminal in your local lab folder. Inside this terminal, `ssh lab-server` connects to your assigned account. Your roll number names your folders; it does not select an account or key. You do not need to install Python or SSH tools on your laptop. If setup fails, see the [troubleshooting instructions](https://github.com/nalinabrol/terminal-lab-4#readme).

The examples use roll number **2026001**. Replace it with your own roll number in every command and path. Use the same Bash commands on Windows, Mac and Linux laptops.

Your local folder is `lab-work/lab4-2026001/` and your server folder is `~/work/lab4-2026001/`, with your roll number in place of `2026001`. Running setup again keeps your existing work. Ask your instructor for help if you need to start over.

| Machine | Folder | Use |
| --- | --- | --- |
| Codespace | `practice/` | Reference files; keep unchanged |
| Codespace | `challenge/project/` | Original project for the final task; keep unchanged |
| Codespace | `work/` | Uploads, downloaded copies, archives and reports |
| Server | `practice/` | Reference files; keep unchanged |
| Server | `work/` | Files for the permission exercises |

The supplied programs print a short message. You will run them without editing their code. Change permissions only on your own working files.

Type commands one at a time. Record your predictions and answers in this booklet or a separate notes file.

## Experiment 1: Connect to the server

**Time:** 10 minutes. **Work on:** your Codespace, in `lab-work/lab4-2026001/`.

Run:

```bash
hostname
whoami
pwd
```

Record the machine name, username and current directory.

Connect to the server:

```bash
ssh lab-server
```

Run the same three commands and compare the results. Then enter your server lab folder and create a file:

```bash
cd ~/work/lab4-2026001
pwd
touch connected.txt
ls -l connected.txt
```

1. Which values changed after connecting?
2. Which machine ran `touch`? Where is `connected.txt` stored?

Return to your local terminal:

```bash
exit
pwd
ls connected.txt
```

The file should be missing here. Reconnect, enter your server lab folder and check that it is still there.

Why does ending the SSH session leave the file on the server?

## Experiment 2: Users, groups and ownership

**Time:** 10 minutes. **Work on:** the server.

```bash
cd ~/work/lab4-2026001/work
whoami
id
ls -l notes.txt
```

`whoami` shows your username. In the output of `id`, find your username and the groups you belong to.

Each file has an owner and an owning group. Find both in the `ls -l` listing for `notes.txt`.

Owner: ____________________  Group: ____________________

Permission string: ____________________

### Who can use this file?

Consider this listing:

```text
-rw-r----- 1 alice students 120 Oct 6 10:00 notes.txt
```

Alice owns the file. Bob belongs to `students`; Charlie does not.

| Person | Permissions used: owner, group or others? | Can read? | Can modify? |
| --- | --- | --- | --- |
| Alice | | | |
| Bob | | | |
| Charlie | | | |

The operating system selects one set of permissions. It uses owner permissions for the owner, group permissions for another member of the owning group, and others for everyone else.

Now change the example: owner permissions are `---` and group permissions are `rw-`. Alice belongs to `students`. Can she read the file? Explain which permissions apply.

## Experiment 3: Change file permissions

**Time:** 15 minutes. **Work on:** the server, in `~/work/lab4-2026001/work`.

Start with:

```bash
chmod 644 notes.txt
ls -l notes.txt
```

The first character shows the file type: `-` means a regular file. The next nine characters give the permissions for owner, group and others.

For a regular file:

| Symbol | Permission |
| --- | --- |
| `r` | Read its contents |
| `w` | Modify its contents |
| `x` | Execute it directly as a program |
| `-` | That permission is absent |

What can each category do with `notes.txt`?

### Add and remove permissions

In `chmod`, `u` selects the owner, `g` the group and `o` others. Use `+` to add a permission and `-` to remove one.

Predict the permission string before each change. Run the commands in order:

```bash
chmod g+w notes.txt
ls -l notes.txt
chmod o-r notes.txt
ls -l notes.txt
```

| Change | Prediction | Result |
| --- | --- | --- |
| Add group write | | |
| Remove others read | | |

Remove your own write permission:

```bash
chmod u-w notes.txt
ls -l notes.txt
```

Will this append succeed? Write your prediction, then try it:

```bash
echo "An extra note" >> notes.txt
```

Record the error. Restore your write permission and append the line:

```bash
chmod u+w notes.txt
echo "An extra note" >> notes.txt
cat notes.txt
```

Why could you use `chmod` when you could not write to the file? Who can normally change a file's permissions?

## Experiment 4: Run a program

**Time:** 10 minutes. **Work on:** the server, in `~/work/lab4-2026001/work`.

`hello.sh` is a supplied program. Check its permissions and try to run it:

```bash
ls -l hello.sh
./hello.sh
```

Record what happens. Add execute permission for the owner and try again:

```bash
chmod u+x hello.sh
ls -l hello.sh
./hello.sh
```

1. What changed in the permission string?
2. What does execute permission allow?
3. Did `chmod` change the program's contents?
4. What does `./` mean in this command?

## Experiment 5: Numeric permissions

**Time:** 10 minutes. **Work on:** the server, in `~/work/lab4-2026001/work`.

```text
read = 4     write = 2     execute = 1     absent = 0
```

Add the values within each category. Read and write give `4 + 2 = 6`.

The three digits represent owner, group and others, in that order. A numeric mode sets all nine basic permission bits.

Predict the permission string for each mode, then check:

```bash
chmod 600 notes.txt
ls -l notes.txt
chmod 644 notes.txt
ls -l notes.txt
chmod 660 notes.txt
ls -l notes.txt
```

| Mode | Prediction | Result |
| --- | --- | --- |
| 600 | | |
| 644 | | |
| 660 | | |

### Choose the modes

Apply a mode that meets each requirement. Check your results with `ls -l`.

| File | Required access | Your mode |
| --- | --- | --- |
| `private.txt` | Owner can read and modify; group and others have no access | |
| `announcement.txt` | Owner can read and modify; group and others can read | |
| `team-notes.txt` | Owner and group can read and modify; others have no access | |

Explain how you calculated one answer. Which group receives access to `team-notes.txt`?

## Experiment 6: Upload and download files

**Time:** 15 minutes. **Work on:** your Codespace. Use `exit` first if you are connected to the server.

Return to your local `lab-work/lab4-2026001/` folder. Check with `pwd`.

`scp` copies files over SSH. The command takes a source followed by a destination: `scp source destination`.

In `lab-server:path`, the path is on the server. The remote paths below are relative to your server home directory.

Create a local file in your Codespace:

```bash
echo "Prepared in my starting terminal" > work/upload.txt
cat work/upload.txt
```

Upload it to the server:

```bash
scp work/upload.txt lab-server:work/lab4-2026001/work/
```

Connect, check the uploaded copy and add a line on the server:

```bash
ssh lab-server
cd ~/work/lab4-2026001/work
cat upload.txt
echo "Edited on the server" >> upload.txt
cat upload.txt
exit
```

Back in your Codespace, download the edited copy into a separate folder. Run these commands in the Codespace lab terminal:

```bash
mkdir work/recovered
scp lab-server:work/lab4-2026001/work/upload.txt work/recovered/
```

Then compare the contents:

```bash
diff work/upload.txt work/recovered/upload.txt
```

If `work/recovered` already exists from an earlier attempt, preserve it under a new name before repeating these steps.

1. Which copy contains the extra line?
2. Did uploading remove the local file?
3. In the download command, which path belongs to which machine?
4. Why does the comparison show a difference?

If you use `.` as the download destination, it means the current directory on the machine where you run `scp`.

## Experiment 7: Deliver a project

**Time:** 15 minutes. **Work on:** your Codespace, in `lab-work/lab4-2026001/`.

The campus event team needs the project stored in `challenge/project/`:

| File | Purpose | Required mode on the server |
| --- | --- | --- |
| `announcement.txt` | Public announcement | 644 |
| `planning-notes.txt` | Private planning notes | 600 |
| `hello.sh` | Program to run after delivery | 700 |

Use the commands from this lab and Lab 3 to complete the delivery.

The Codespace has `zip`, `unzip` and `tar` installed. Use the Bash commands from Lab 3. Inspect the archive after delivery to check its paths.

1. Create a ZIP or gzip-compressed tar archive containing the `project/` folder. Save it as `work/project.zip` or `work/project.tar.gz` in your local lab folder. Choose your working directory so extraction produces a top-level `project/` folder.
2. Connect to the server and create `challenge-delivery` inside your server lab folder. Return to your local terminal and upload the archive there.
3. Reconnect, enter `challenge-delivery`, list the archive's contents and extract it.
4. Set the three file modes shown above. Check them and run `hello.sh` from the extracted project folder.
5. From `challenge-delivery`, save the output of `ls -l project` as `permissions-report.txt`.
6. Return to your Codespace and download the report into your local `work/` folder.

Keep `challenge/project/` unchanged. If you repeat the delivery, move the old server `challenge-delivery` folder to an unused backup name first, or ask your instructor for help. The checker expects the completed delivery at `challenge-delivery`.

### Show your work

Show the server's file listing and the program output to your instructor. Download `lab-work/lab4-YOUR-ROLL/work/permissions-report.txt` from the Codespace Explorer to your physical laptop (right-click the file and choose **Download**). Submit it using the class submission instructions.

Be ready to explain:

- Where you created the archive, extracted it and ran the program.
- Why each file has its assigned mode.
- Whether inspecting a downloaded file's permissions tells you the permissions of the server copy. How would you check the server copy?

## Check your work

**Time:** 5 minutes.

From your local `lab-work/lab4-2026001/` folder in the Codespace lab terminal, run:

```bash
check_lab
```

The checker uses your SSH connection to check saved files and server permissions. Read any `CHECK` messages, correct the results and run it again. It keeps your files unchanged and does not submit your work.

Your instructor may ask you to connect, identify the current machine, change a permission or demonstrate a transfer.

### Before you finish

1. How can you tell whether your commands are running in your Codespace or on the server?
2. A file has owner permissions `---` and group permissions `rw-`. Can its owner use the group permissions instead?
3. How does `chmod g+w file` differ from `chmod 660 file`?
4. How would you check that a file reached the intended server folder?
