# Problems Encountered

A record of specific technical issues faced while completing this project, how each was diagnosed, and how it was resolved.

---

## 1. VS Code Couldn't Open a Linux (WSL) Folder Through the Normal "Open Folder" Dialog

**Problem:**
Trying to open a Linux project folder (`linux_assignment`) located inside the Ubuntu home directory using VS Code's **File → Open Folder** menu. The dialog that appeared only showed Windows drives (C:, This PC) — the Linux/WSL file path never appeared, and manually typing the Linux path into that window either failed or froze.

**Root cause:**
VS Code's standard "Open Folder" dialog is a native **Windows** file picker. Windows does not natively browse the WSL (Linux) filesystem the same way it browses local drives — it treats the Linux filesystem more like a hidden network location, which makes the normal "click and browse" method unreliable.

**Fix — bypass the dialog entirely, launch VS Code from inside Linux itself:**

```bash
# Step 1: Open the Ubuntu terminal and navigate to the project folder
cd ~/linux_assignment

# Step 2: Launch VS Code directly from that location
code .
```

On first run, VS Code shows a security prompt asking whether to trust the connection to `wsl.localhost`. Check **"Permanently allow host"** and click **Allow**. VS Code then reloads and correctly loads the folder, with all files visible in the sidebar.

**What `code .` actually means:**
- `code` — the command that launches VS Code
- `.` — in Linux, this means "the current directory — right here"

So `code .` translates literally to: *"Open VS Code, loaded into the exact folder I'm currently standing in."*

---

## 2. Couldn't Locate the Correct Terraform Provider Block for GCP

**Problem:**
While setting up `main.tf`, the correct Terraform provider block syntax for Google Cloud Platform (GCP) wasn't easy to locate directly on the official HashiCorp Registry documentation.

**Resolution:**
Cross-referenced multiple sources — the instructor's own recorded session, Medium articles, and community write-ups — to confirm the correct provider block syntax before adding it to `main.tf`.

**Lesson:** official documentation isn't always the fastest or clearest starting point — cross-referencing a walkthrough video or well-written community article alongside the official docs often clarifies the exact syntax faster.

---

## 3. `gcloud: command not found` — Google Cloud CLI Not Installed

**Problem:**
Running the standard authentication command:
```bash
gcloud auth application-default login
```
returned:
```
bash: gcloud: command not found
```

**Root cause:**
The Google Cloud CLI (`gcloud`) was never installed on the local machine. Terraform requires `gcloud` to be installed and available on the system PATH in order to authenticate with GCP via Application Default Credentials (ADC).

**Resolution steps:**
1. Downloaded the Google Cloud CLI installer for Windows from `cloud.google.com/sdk/docs/install`
2. Ran the installer to completion
3. Added the `gcloud` binary path to the Windows system environment variables (PATH)
4. Closed and reopened the VS Code terminal to reload the updated PATH
5. Verified installation:
   ```bash
   gcloud --version
   ```
6. Successfully re-ran:
   ```bash
   gcloud auth application-default login
   ```
   which opened a browser window for Google account authentication.

---

## 4. Warning After Authentication: "Cannot Find a Quota Project"

**Problem:**
Immediately after successful authentication, this warning appeared:
```
WARNING: Cannot find a quota project to add to ADC.
You might receive a "quota exceeded" or "API not enabled" error.
Run $ gcloud auth application-default set-quota-project to add a quota project.
```
This initially looked like it might block Terraform from running.

**Investigation:**
Research (including Stack Overflow discussions) clarified the following:
- This is a **warning**, not an error — authentication had already succeeded, and the credentials file was confirmed and saved
- A **quota project** is the GCP project that API usage/billing is tracked against
- The warning appeared because the authenticated account had **limited IAM permissions** on the shared training project, and `gcloud` could not automatically set a quota project as a result
- Attempting to manually set a quota project returned a permissions error, which confirmed the account's restricted access was intentional/by design, not a bug

**Resolution:**
The warning was safely ignored. Since the `provider` block in `main.tf` already explicitly declares the target `project` ID, Terraform used that directly and did not depend on a CLI-level quota project being set. `terraform init`, `terraform plan`, and `terraform apply` all completed successfully despite the warning.

---

## 5. Airflow Couldn't Find the Local Data File — Docker Container Path vs. Host Machine Path

**Problem:**
Referencing the source CSV file using a normal relative path (e.g. `./dags/data/users_clean.csv`, or an actual Windows path like `C:\Users\...\dags\data\users_clean.csv`) inside `config.py` resulted in Airflow being unable to find the file at all when the DAG ran.

**Root cause:**
Astronomer's Airflow runs entirely inside a **Docker container** — not directly on the host machine. When `astro dev start` runs, the entire project is compiled and copied into that container's own internal filesystem, which is completely separate from the Windows (or WSL) filesystem the project files were originally written in. A host-machine path has no meaning inside the container; Airflow only ever reads files from its own container filesystem.

**Resolution — resolve the correct path from inside the running container itself:**

```bash
# Open a shell directly inside the running Airflow container
astro dev bash

# Navigate to the folder where the data file lives
cd dags/data

# Print the actual, full path as seen from inside the container
pwd
```

This produced the real, usable path:
```
/usr/local/airflow/dags/data/users_clean.csv
```

That container path — not any Windows or WSL path — is what was used in `config.py`:
```python
DATA_SOURCE_PATH = "/usr/local/airflow/dags/data/users_clean.csv"
```

**Lesson:** any time a Dockerized tool (Airflow included) needs to reference a file on disk, the path must always be resolved from *inside* that container using a command like `astro dev bash`, never assumed from the host machine's own folder structure — even though the file appears in the same place inside your code editor.

---

## Summary Table

| # | Issue | Category | Root Cause | Resolution |
|---|---|---|---|---|
| 1 | VS Code can't open WSL folder via dialog | Environment / Tooling | Windows file picker can't browse WSL filesystem | Launch VS Code from inside Linux using `code .` |
| 2 | Couldn't find GCP provider block syntax | Documentation | Not clearly surfaced on HashiCorp Registry | Cross-referenced instructor video + community articles |
| 3 | `gcloud: command not found` | Missing Dependency | Google Cloud CLI not installed | Installed CLI, added to PATH, reloaded terminal |
| 4 | "Cannot find a quota project" warning | GCP IAM / Permissions | Limited IAM permissions on shared training project | Safely ignored — project ID explicitly set in provider block |
| 5 | Airflow can't find local CSV file | Docker / Filesystem | Used host path instead of container path | Used `astro dev bash` + `pwd` to get correct container path |