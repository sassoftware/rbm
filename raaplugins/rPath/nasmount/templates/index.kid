<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import raa.templates.master ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="raa.templates.master">
<!--
    Copyright (c) 2007 rPath, Inc.
    All Rights Reserved
-->
<head>
  <title>Remote Conary Contents Store</title>
</head>
<body>
    <div class="mount">
        <p><h3>Remote Contents Store</h3></p>
        <div py:if="not (server or remoteMount)">
            <h5>Use this page to manage remote storage settings for the Conary repository contents on the rPath Update Service appliance. Type the NFS server name and the exported filesystem in the fields provided.</h5>
            <p>
                <hr />
            </p>
            <form action="setMount" method="POST">
                <table>
                    <tr>
                        <td>NFS Server:</td><td><input type="text" name="server"/></td>
                    </tr>
                    <tr>
                        <td>Exported Filesystem:</td><td><input type="test" name="remoteMount"/></td>
                    </tr>
                </table>
                <input class="button" type="submit" value="Save"/>
            </form>
        </div>
        <div py:if="server or remoteMount">
            <h5>It is not possible to change the remote storage settings for the Conary repository contents on the rPath Update Service appliance. The current settings are:</h5>
            <p>
                <hr />
            </p>
            <table>
                <tr>
                    <td>NFS Server:</td><td>${server}</td>
                </tr>
                <tr>
                    <td>Exported Filesystem:</td><td>${remoteMount}</td>
                </tr>
            </table>
        </div>
    </div>
</body>
</html>
