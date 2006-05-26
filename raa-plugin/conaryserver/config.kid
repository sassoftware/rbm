<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import raa.templates.master ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="raa.templates.master">
<!--
    Copyright (c) 2005-2006 rPath, Inc.
    All Rights Reserved
-->
<head>
    <title>Set the Conary Server Hostname</title>
    <style type="text/css">
        tr#oddRow {
            background: #c7d7ff;
            text-decoration: italic;
            right-padding: 0px;
        }
        tr#evenRow {
            background: #ffffff;
            text-decoration: italic;
            right-padding: 0px;
        }
    </style>
</head>

<body>
        <h2>Update Conary Repository Server Hostnames</h2>
        <p>${pageText}</p>
        <hr />
            <label for="servername"><h4>New Conary Repository Server Hostname:</h4></label>
            <input type="text" id="servername" name="newsrv" style="width: 75%; float: left;"/>
            <button type="submit"  class="img"><img alt="Add" src="${tg.url('/static/images/add_button.png')}"/></button>
        <br/><br/><br/>

        <h4>Current Conary Repository Server Hostnames:</h4>
        <table class="list">
            <?python rowType = 1 ?>
            <tr py:for="host in data" id="${rowType and 'oddRow' or 'evenRow'}">
            <td>${host}</td>
            <td><a href="delete">Delete</a></td>
            <?python rowType = rowType ^ 1 ?>
            </tr>
        </table>
</body>
</html>
