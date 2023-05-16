
Write-Host "vSphere Powercli Script was startet"
write-host "creating vlan "  $args[1] "with name "  $args[2]
write-host "Running vSphere powershell to: "  $args[0]

connect-viserver $args[0]
 
$Clusters = @(
  "Default",
  "Medical"
)
 
 
foreach ($cl in $Clusters) {
 
  $VMHosts = get-Cluster $cl | get-vmhost
 
  foreach ($SRV in $VMHosts) {
    write-host $SRV
    Get-VMHost -name $SRV | Get-VirtualSwitch -name vSwitch1 | New-VirtualPortGroup -Name $args[2] -VLanId $args[1] -whatif
  }
}