transaction-anomaly-detector
a proof-of-concept script for flagging suspicious transactions based on a simple ruleset (amount, country, etc.). powershell setup and basic commands guide
this guide provides a complete, step-by-step walkthrough for installing, configuring, and using powershell on windows. it’s designed for absolute beginners—even if you’re new to command lines, you’ll get it. we’ll cover installation, setup, essential commands for file management, processes, networking, package installation, and creating a simple automation script. all commands are for powershell 7+ (the modern version).
prerequisites
•
windows 10 or 11.
•
administrator access for some steps.
•
open powershell as admin: right-click start → “windows powershell (admin)” or search for “pwsh” after installation.
step 1: install powershell 7
powershell 5.1 comes pre-installed, but powershell 7 is better (cross-platform, faster).
1.
if you have winget (built into recent windows), open powershell as admin and run:
POWERSHELL
2 lines
winget install --id microsoft.powershell --source winget
2.
if no winget, download from github (microsoft/powershell) and run the .msi or .exe installer.
3.
alternatively, install from microsoft store: search for “powershell”.
4.
restart your terminal. verify version: pwsh -v (launches powershell 7).
step 2: basic configuration
launch powershell 7 by typing pwsh in the start search and pressing enter.
1.
set execution policy to allow scripts (safer than unrestricted):
POWERSHELL
2 lines
set-executionpolicy remotesigned -scope currentuser
confirm with ‘y’ if prompted. this lets you run local scripts without signing.
2.
install useful modules (e.g., for git integration):
POWERSHELL
3 lines
install-module posh-git -scope currentuser
import-module posh-git
3.
create a profile for auto-loading settings (optional but handy):
POWERSHELL
2 lines
if (!(test-path -path $profile)) { new-item -itemtype file -path $profile -force }
open it: notepad $profile. add custom commands (e.g., aliases like set-alias ll get-childitem), save, and restart powershell.
step 3: essential commands
enter these one by one in powershell. use tab for auto-completion and get-help for more info.
file and directory management
•
list files in current directory: get-childitem (alias: ls or dir).
•
create a directory: new-item -itemtype directory -path c:\myfolder.
•
copy a file: copy-item source.txt destination.txt.
•
delete a file: remove-item file.txt (alias: rm file.txt). use -recurse -force for folders.
•
read a file: get-content file.txt (alias: cat file.txt).
•
write to a file: set-content file.txt "your text here".
process management
•
list running processes: get-process (alias: ps).
•
kill a process: stop-process -name notepad (e.g., close notepad).
•
start a program: start-process notepad.exe.
networking and system info
•
get your ip address: get-netipaddress | select ipaddress.
•
test connection: test-netconnection google.com -port 80.
•
list services: get-service.
•
restart computer: restart-computer (requires admin).
package management (install/upgrade software)
use winget (built-in) or install chocolatey for more options.
1.
install chocolatey (one-time, as admin):
POWERSHELL
2 lines
set-executionpolicy bypass -scope process -force; [system.net.servicepointmanager]::securityprotocol = [system.net.servicepointmanager]::securityprotocol -bor 3072; iex ((new-object system.net.webclient).downloadstring('https://community.chocolatey.org/install.ps1'))
2.
install software: choco install vscode (e.g., visual studio code).
3.
upgrade all: winget upgrade --all or choco upgrade all -y.
step 4: create and run a simple automation script
automate common tasks with a script file.
1.
create script file: new-item -itemtype file -path myscript.ps1.
2.
edit it: notepad myscript.ps1. paste this example (save):
POWERSHELL
10 lines
# simple script: lists files, processes, and ip
write-host "files in current directory:"
get-childitem

write-host "running processes (top 5 by cpu):"
get-process | sort-object cpu -descending | select-object -first 5 | select name, id, cpu

write-host "your ip address:"
get-netipaddress | where-object {$_.addressfamily -eq 'ipv4'} | select ipaddress
3.
run it: navigate to the folder (cd c:\path\to\script), then .\myscript.ps1.
•
if blocked: check execution policy (step 2).
•
for scheduling: use task scheduler. command: schtasks /create /tn "mydailytask" /tr "pwsh -file c:\myscript.ps1" /sc daily /st 09:00.
tips for beginners
•
always run as admin for system changes (right-click → run as administrator).
•
errors? copy the message and search it—powershell errors are descriptive.
•
learn pipelines for power: get-process | where-object {$_.cpu -gt 100} | stop-process (stops high-cpu processes).
•
security: don’t run untrusted scripts. use -whatif flag to preview actions (e.g., remove-item file.txt -whatif).
