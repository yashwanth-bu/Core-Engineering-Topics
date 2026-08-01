# Java Version Switching

This guide explains how to switch between multiple installed Java versions using Windows batch (`.bat`) files.

## Prerequisites

* Install one or more JDK versions on your machine.
* Know the installation path of each JDK.

Example JDK installation paths:

```text
C:\Program Files\Java\jdk-<version>
C:\Users\<username>\AppData\Local\Programs\Eclipse Adoptium\jdk-<version>
```

Replace `<version>` with the installed JDK version (for example: `17`, `21`, `25`, etc.).

---

## Batch File Template

Create one batch file for each Java version.

```bat
@echo off
set JAVA_HOME=<JDK_INSTALLATION_PATH>
set PATH=%JAVA_HOME%\bin;%PATH%
java -version
```

Replace:

```text
<JDK_INSTALLATION_PATH>
```

with the path to the desired JDK.

Example file names:

```text
Use-Java17.bat
Use-Java21.bat
Use-Java25.bat
```

---

## How It Works

Each batch file:

1. Sets the `JAVA_HOME` environment variable.
2. Places the selected JDK's `bin` directory at the beginning of the `PATH`.
3. Verifies the active Java version by running:

```cmd
java -version
```

These changes affect **only the current Command Prompt session**. They do **not** permanently modify your Windows environment variables.

---

## Using the Scripts

Run the batch file for the Java version you want to use.

Example:

```cmd
Use-Java17.bat
```

Then verify:

```cmd
java -version
echo %JAVA_HOME%
where java
```

---

## Adding a New Java Version

1. Install the new JDK.
2. Copy an existing batch file.
3. Update the `JAVA_HOME` path.
4. Rename the file (for example, `Use-Java21.bat`).
5. Run the script and verify with `java -version`.

---

## Notes

* The selected Java version is available only in the Command Prompt where the script was executed.
* Opening a new Command Prompt restores your default Java configuration.
* This approach lets you switch between multiple JDK versions without changing the system-wide environment variables.
