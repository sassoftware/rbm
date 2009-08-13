<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python 
import raa.templates.master
from raa.web import makeUrl
?>
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
    <div class="plugin-page" id="plugin-page">
      <div class="page-content"> 
        <div py:strip="True" py:if="key" class="page-content-section">
        <p>Please provide the following information to your rEA 
        administrator. <span py:if="len(serverNames) > 1">Note that 
        a separate Provider and Service must be created for each Provider
        Name.</span></p>
        <table class="list" cellspacing="0" py:for="serverName in serverNames">
          <tr>
            <td>Provider Name:</td>
            <td>${serverName}</td>
          </tr>
          <tr>
            <td>Resource Type:</td>
            <td>rPath Update Service</td>
          </tr>
          <tr>
            <td>Entitlement Class:</td>
            <td>management</td>
          </tr>
          <tr>
            <td>Entitlement Key:</td>
            <td>${key}</td>
          </tr>
          <tr>
            <td>Host:</td>
            <td>${hostName}</td>
          </tr>
        </table>
        </div>
        <div class="page-section-content">
        <br />
        <p>To change the administrative entitlement, use the form below.
        The <b>Generate</b> button will create a new random key, or you may enter a key of your choosing.</p>
        </div>
        <div py:if="not key">
          <div class="page-section-content">
          Use this page to create a new administrative entitlement for an
          rPath Entitlement Appliance (rEA).
          </div>
          <div class="page-section">First installation</div>
          <div class="page-section-content">
          Click <b>Generate</b> to create a new entitlement for an rPath
          Entitlement Appliance, and then click <b>OK</b> to save it.<br/>
          </div>
          <div class="page-section">Restoring from a failure</div>
          <div class="page-section-content">
          Type or paste the previously generated entitlement in the text
          box and click <b>OK</b>.
          </div>
        </div>
        <form name="page_form" action="setkey" method="POST">
          <div class="page-section-content">
            <div class="form-line" style="width: 550px">
              <a class="rnd_button float-right" id="Generate" onclick="genKey();" href="javascript:void(0);">Generate</a>
              <br />
            </div>
            <div class="form-line">
              <label for="key_field" class="pwd-label-div">Entitlement:</label>
              <input id="key_field" type="text" name="key" size="40" value="${key}" class="pwd-input" style="width: 400px;" />
            </div>
            <div class="form-line" style="width: 550px">
              <a class="rnd_button float-right" id="OK" href="javascript:button_submit(document.page_form)">OK</a>
            </div>
          </div>
        </form>
      </div>
    </div>
</body>
</html>
