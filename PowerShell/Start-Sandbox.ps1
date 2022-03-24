#requires -version 2

<#
.SYNOPSIS
    Starts a sandbox with provided configuration options.

.DESCRIPTION
    Uses provided configuration options to create a temporary .wsb file. Windows Sandbox is then started with this configuration.

.PARAMETER vGPU
    Enable or disable vGPU. If not provided default is used.

.PARAMETER Networking
    Disable networking. If not provided default is used.

.PARAMETER MappedFolders
    Array of folders to map in the sandbox. Input should be an array of hashmaps with keys HostFolder, SandboxFolder and ReadOnly.

.PARAMETER LogonCommand
    Command to execute upon logging on.

.PARAMETER AudioInput
    Enable or disable audio input. If not provided default is used.

.PARAMETER VideoInput
    Enable or disable video input. If not provided default is used.

.PARAMETER ProtectedClient
    Enable or disable protected client. If not provided default is used.

.PARAMETER PrinterRedirection
    Enable or disable printer redirection. If not provided default is used.

.PARAMETER ClipboardRedirection
    Disable clipboard redirection. If not provided default is used.

.PARAMETER MemoryInMB
    The memory to be used in MB.

.INPUTS
    None.

.OUTPUTS
    None.
#>

param (
    [string][ValidateSet('Enable', 'Disable')] $vGPU = 'Default',
    [string][ValidateSet('Disable')] $Networking = 'Default',
    [hashtable[]] $MappedFolders,
    [string] $LogonCommand,
    [string][ValidateSet('Enable', 'Disable')] $AudioInput = 'Default',
    [string][ValidateSet('Enable', 'Disable')] $VideoInput = 'Default',
    [string][ValidateSet('Enable', 'Disable')] $ProtectedClient = 'Default',
    [string][ValidateSet('Enable', 'Disable')] $PrinterRedirection = 'Default',
    [string][ValidateSet('Disable')] $ClipboardRedirection = 'Default',
    [int] $MemoryInMB = 0
)

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