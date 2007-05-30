<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import raa.templates.master ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="raa.templates.master">

<!--
    Copyright (c) 2006 rPath, Inc.
    All Rights Reserved
-->

<head>
    <title>Manage Administrative Entitlement</title>
    <script type="text/javascript">
        function genKey() {
            var allowed = 'abcdefghijklmnopqrstuvwxyz0123456789';
            var length = 56;
            var key = new String();
            for (var i = 0; length > i; i++) {
                key += allowed.charAt(Math.floor(Math.random()*(allowed.length+1)));
            }
            var field = document.getElementById('key_field');
            field.value = key;
        }
    </script>
</head>

<body>
    <h3>Manage Administrative Entitlement</h3>
        <h5>Use this page to create a new administrative entitlement for an
        rPath Entitlement Appliance (rEA).<br/><br/>
        <u>First installation</u><br/>
        Click <u>Generate</u> to create a new entitlement for an rPath
        Entitlement Appliance, and then click <u>OK</u> to save it.<br/><br/>
        <u>Restoring from a failure</u><br/>
        Type or paste the previously generated entitlement in the text
        box and click <u>OK</u>.<br/>
        <div py:strip="True" py:if="key">
            <br/>
            <p>Please provide the following information to your rEA 
            administrator. <span py:if="len(serverNames) > 1">Note that 
            a separate service must be created for each Repository Hostname.</span></p>
            <table class="list" cellspacing="0" py:for="serverName in serverNames">
                <tr>
                    <td>Resource Type:</td>
                    <td>rBuilder Mirror</td>
                </tr>
                <tr>
                    <td>Repository Hostname:</td>
                    <td>${serverName}</td>
                </tr>
                <tr>
                    <td>Server URL:</td>
                    <td>https://${hostName}/conary/</td>
                </tr>
                <tr>
                    <td>Entitlement Class:</td>
                    <td>management</td>
                </tr>
                <tr>
                    <td>Entitlement:</td>
                    <td>${key}</td>
                </tr>
            </table>
        </div></h5>

    <form action="setkey" method="POST">
        <table>
            <tr>
                <td></td>
                <td style="text-align: right;">
                    <a onclick="genKey();" href="javascript:void(0);"><button class="img"><img src="${tg.url('/static/images/generate.png')}" alt="Generate" /></button></a>
                </td>
            </tr>
            <tr>
                <td class="label">
                    <label>Entitlement:</label>
                </td>
                <td class="field">
                    <input id="key_field" type="text" name="key" size="40" value="${key}" />
                </td>
            </tr>
            <tr>
                <td></td>
                <td>
                </td>
            </tr>
        </table>
        <button class="img" type="submit">
            <img src="${tg.url('/static/images/ok_button.png')}" value="OK" />
        </button>

    </form>

</body>
</html>
