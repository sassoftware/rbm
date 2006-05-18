<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<? python import raa.templates.master ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="raa.templates.master">
<!--
    Copyright (c) 2005-2006 rPath, Inc.
    All Rights Reserved
-->
<head>
    <title>Update Conary Server Hostname</title>
</head>


<body>
    <div id="UpdateComplete">
        <h2>Update Conary Server Hostname</h2>
        <span py:if="errorState">
            <font color="#FF0000">
            <p>${pageText}</p>
            </font>
        </span>
        <span py:if="not errorState">
            <p>${pageText}</p>
        </span>
        <hr />
        <p><h3>Current Conary Server Hostname:</h3>
            <i>${srvname}</i>
        </p>
        <br />
        <br />
        <hr />
    </div>
</body>
</html>
