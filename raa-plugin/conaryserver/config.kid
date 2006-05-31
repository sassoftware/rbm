<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import raa.templates.master ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="raa.templates.master">
<!--
    Copyright (c) 2005-2006 rPath, Inc.
    All Rights Reserved
-->
<head>
    <title>Update Repository Server Names</title>
    <style type="text/css">
        tr#oddRow {
            background: #c7d7ff;
            font-style: italic;
        }
        tr#evenRow {
            background: #ffffff;
            font-style: italic;
        }
        h5#success {
            background: #D7FFD4;
            border-width: 1px;
            border-style: solid;
            border-color: #61b75a;
            padding: 5px;
        }
        h5#error {
            background: #FFDFD4;
            border-width: 1px;
            border-style: solid;
            border-color: #ff8077;
            padding: 5px;
        }
    </style>
</head>

<body>
        <h2>Update Repository Server Names</h2>
        <h5 id="${errorState}">${XML(pageText)}</h5>
        <hr />
        <form action="setsrvname" method="post">
            <label for="servername"><h4>New Repository Server Name:</h4></label>
            <input type="text" id="servername" name="srvname" style="width: 75%; float: left;"/>
            <button type="submit"  class="img"><img alt="Add" src="${tg.url('/static/images/add_button.png')}"/></button>
        </form>
        <br/><br/><br/>

        <h4 py:if="data">Current Repository Server Names:</h4>
        <table class="list">
            <?python rowType = 1 ?>
            <tr py:for="host in data" id="${rowType and 'oddRow' or 'evenRow'}">
            <td>${host[0]}</td>
            <td ><form py:if="host[1]" action="delsrvname" method="post"><input type="hidden" name="srvname" value="${host[0]}"/><button class="img" type="submit"><img src="${tg.url('/static/images/close16x16.png')}" value="Delete"/></button></form></td>
            <?python rowType = rowType ^ 1 ?>
            </tr>
        </table>
</body>
</html>
