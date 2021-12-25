#requires -version 2

<#
.SYNOPSIS
    Starts a sandbox with provided configuration options.

.DESCRIPTION
    Uses provided configuration options to create a temporary .wsb file. Windows Sandbox is then started with this configuration.

.PARAMETER vGPU
    If True turns on vGPU. False disables it. For any other value default setting is used.

.PARAMETER Networking
    If True turns on networking. False disables it. For any other value default setting is used.

.PARAMETER MappedFolders
    Array of folders to map in the sandbox. Input should be an array of hashmaps with keys HostFolder, SandboxFolder and ReadOnly.

.PARAMETER LogonCommand
    Command to execute upon logging on.

.PARAMETER AudioInput
    If True turns on audio input. False disables it. For any other value default setting is used.

.PARAMETER VideoInput
    If True turns on video input. False disables it. For any other value default setting is used.

.PARAMETER ProtectedClient
    If True turns on protected client. False disables it. For any other value default setting is used.

.PARAMETER PrinterRedirection
    If True turns on printer redirection. False disables it. For any other value default setting is used.

.PARAMETER ClipboardRedirection
    If True turns on clipboard redirection. False disables it. For any other value default setting is used.

.PARAMETER MemoryInMB
    The memory to be used in MB.

.INPUTS
    None.

.OUTPUTS
    None.
#>

param (
    [string] $vGPU,
    [string] $Networking,
    [hashtable[]] $MappedFolders,
    [string] $LogonCommand,
    [string] $AudioInput,
    [string] $VideoInput,
    [string] $ProtectedClient,
    [string] $PrinterRedirection,
    [string] $ClipboardRedirection,
    [int] $MemoryInMB
)

# Normalize parameter values.
$vGPU = $vGPU.ToLower()
if ($vGPU -eq "true" -or $vGPU -eq "on" -or $vGPU -eq "yes" -or $vGPU -eq "1") {
    $vGPU = "Enable"
}
elseif ($vGPU -eq "false" -or $vGPU -eq "off" -or $vGPU -eq "no" -or $vGPU -eq "0") {
    $vGPU = "Disable"
}
else {
    $vGPU = "Default"
}

$Networking = $Networking.ToLower()
if ($Networking -eq "false" -or $Networking -eq "off" -or $Networking -eq "no" -or $Networking -eq "0") {
    $Networking = "Disable"
}
else {
    $Networking = "Default"
}

$AudioInput = $AudioInput.ToLower()
if ($AudioInput -eq "true" -or $AudioInput -eq "on" -or $AudioInput -eq "yes" -or $AudioInput -eq "1") {
    $AudioInput = "Enable"
}
elseif ($AudioInput -eq "false" -or $AudioInput -eq "off" -or $AudioInput -eq "no" -or $AudioInput -eq "0") {
    $AudioInput = "Disable"
}
else {
    $AudioInput = "Default"
}

$VideoInput = $VideoInput.ToLower()
if ($VideoInput -eq "true" -or $VideoInput -eq "on" -or $VideoInput -eq "yes" -or $VideoInput -eq "1") {
    $VideoInput = "Enable"
}
elseif ($VideoInput -eq "false" -or $VideoInput -eq "off" -or $VideoInput -eq "no" -or $VideoInput -eq "0") {
    $VideoInput = "Disable"
}
else {
    $VideoInput = "Default"
}

$ProtectedClient = $ProtectedClient.ToLower()
if ($ProtectedClient -eq "true" -or $ProtectedClient -eq "on" -or $ProtectedClient -eq "yes" -or $ProtectedClient -eq "1") {
    $ProtectedClient = "Enable"
}
elseif ($ProtectedClient -eq "false" -or $ProtectedClient -eq "off" -or $ProtectedClient -eq "no" -or $ProtectedClient -eq "0") {
    $ProtectedClient = "Disable"
}
else {
    $ProtectedClient = "Default"
}

$PrinterRedirection = $PrinterRedirection.ToLower()
if ($PrinterRedirection -eq "true" -or $PrinterRedirection -eq "on" -or $PrinterRedirection -eq "yes" -or $PrinterRedirection -eq "1") {
    $PrinterRedirection = "Enable"
}
elseif ($PrinterRedirection -eq "false" -or $PrinterRedirection -eq "off" -or $PrinterRedirection -eq "no" -or $PrinterRedirection -eq "0") {
    $PrinterRedirection = "Disable"
}
else {
    $PrinterRedirection = "Default"
}

$ClipboardRedirection = $ClipboardRedirection.ToLower()
if ($ClipboardRedirection -eq "false" -or $ClipboardRedirection -eq "off" -or $ClipboardRedirection -eq "no" -or $ClipboardRedirection -eq "0") {
    $ClipboardRedirection = "Disable"
}
else {
    $ClipboardRedirection = "Default"
}

# Create xml for mapped folders.
$MappedFoldersXml = "<MappedFolders>"
foreach ($MappedFolder in $MappedFolders) {
    $HostFolder = $MappedFolder["HostFolder"]
    $SandboxFolder = $MappedFolder["SandboxFolder"]
    $ReadOnly = if ($MappedFolder["ReadOnly"]) { $MappedFolder["ReadOnly"].ToString().ToLower() } else { "" }
    $ReadOnly = if ($ReadOnly -eq "true" -or $ReadOnly -eq "on" -or $ReadOnly -eq "yes" -or $ReadOnly -eq "1") { "true" } else { "false" }
    $MappedFoldersXml += @"
    <MappedFolder>
        <HostFolder>$HostFolder</HostFolder>
        <SandboxFolder>$SandboxFolder</SandboxFolder>
        <ReadOnly>$ReadOnly</ReadOnly>
    </MappedFolder>
"@
}
$MappedFoldersXml += "</MappedFolders>"

# Create xml for logon command.
if ($LogonCommand -ne "") {
    $LogonCommandXml = @"
    <LogonCommand>
        <Command>$LogonCommand</Command>
    </LogonCommand>
"@
}
else {
    $LogonCommandXml = ""
}

# Create xml for memory.
$MemoryInMBXml = if ($MemoryInMB -gt 0) { "<MemoryInMB>$MemoryInMB</MemoryInMB>" } else { "" }

# Create configuration xml.
$WSBText = @"
<Configuration>
    <vGPU>$vGPU</vGPU>
    <Networking>$Networking</Networking>
    $MappedFoldersXml
    $LogonCommandXml
    <AudioInput>$AudioInput</AudioInput>
    <VideoInput>$VideoInput</VideoInput>
    <ProtectedClient>$ProtectedClient</ProtectedClient>
    <PrinterRedirection>$PrinterRedirection</PrinterRedirection>
    <ClipboardRedirection>$ClipboardRedirection</ClipboardRedirection>
    $MemoryInMBXml
</Configuration>
"@

$WSBFile = Join-Path $Env:TEMP "Sandbox.wsb"

Out-File -InputObject $WSBText -FilePath $WSBFile

Start-Process WindowsSandbox.exe $WSBFile