<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import raa.templates.master ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="raa.templates.master">

<!--
    Copyright (c) 2006 rPath, Inc.
    All Rights Reserved
-->

<head>
    <title>rEA Entitlement</title>
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
    <h3>rEA Entitlement Management</h3>
    <h5><p>Add a new rEA entitlement key, or modify the existing key by entering
        a valid key value into the Entitlement key text input field, and
        clicking OK to save.  If you do not already have a key, you can 
        create one by clicking Generate.</p>
        <p py:if="key">Your current rEA key is: <em>${key}</em></p></h5>
    <form action="setkey" method="POST">
        <table>
            <tr>
                <td></td>
                <td style="text-align: right;">
                    <a onclick="genKey();" href="javascript:void(0);">Generate</a>
                </td>
            </tr>
            <tr>
                <td class="label" style="width: 35%;">
                    <label>rEA Entitlement key:</label>
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
