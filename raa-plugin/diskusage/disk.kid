<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import raa.templates.master ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="raa.templates.master">
<!--
    Copyright (c) 2005-2006 rPath, Inc.
    All Rights Reserved
-->
<head>
    <title>Disk Usage</title>
    <style type="text/css">
        <!--
        div#colHeader {
            float: left;
            width: 16%;
            font-weight: bold;
            text-decoration: underline;
            text-align: center;
        }

        div#colEntry {
            float: left;
            width: 16%;
            text-align: center;
        }
        -->
    </style>
</head>


<body id="middleWide">
    <div>
        <h3>Disk Usage</h3>
        <div id="colHeader">Filesystem</div>
        <div id="colHeader">Size</div>
        <div id="colHeader">Used</div>
        <div id="colHeader">Available</div>
        <div id="colHeader">Percent Used</div>
        <div id="colHeader">Mounted On</div>
        <br/><br/>
        <div py:for="line in data">
            <div id="colEntry" py:for="word in line">${word}</div>
        <br/>
        </div>
    </div>
</body>
</html>
