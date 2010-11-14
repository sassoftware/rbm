<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python 
import raa.templates.master
from raa.web import makeUrl
?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="raa.templates.master">

<!--
    Copyright (c) 2010 rPath, Inc.
    All Rights Reserved
-->

<head>
  <title>Proxy / Mirror Setup</title>
  <script type="text/javascript">
  function configureRBAHostname()
  {
    var proxymode = document.getElementById('_mode_proxy').checked;
    var rbaHostname = document.getElementById("rbaHostname");

    rbaHostname.disabled = (proxymode == true) ? false : true;
  }
  </script>
</head>

<body>
    <div class="plugin-page" id="plugin-page">
      <form name="page_form" action="javascript:void(0);" method="POST" onsubmit="javascript:postFormWizardRedirectOnSuccess(this, 'setMode');">
      <div class="page-content"> 
        <div py:strip="True" class="page-content-section">
          <div class="form-line-top">Please choose which mode of operation this rPath Update Service should use</div>
          <div class="form-line">
            <input type="radio" name="mode" id="_mode_mirror" py:attrs="(mode == 'mirror') and {'checked': 'checked'} or {}" onclick="javascript:configureRBAHostname();" value="mirror" /><label for="mode"><b>Mirror Mode</b>should be used when ....</label>
          </div>
          <div class="form-line">
            <input type="radio" name="mode" id="_mode_proxy" py:attrs="(mode == 'proxy') and {'checked': 'checked'} or {}" onclick="javascript:configureRBAHostname();" value="proxy" /><label for="mode"><b>Proxy Mode</b> should be used when ....</label>
          </div>
          <div class="form-line">
            <div class="host-label-div">rBuilder Hostname (for proxy mode):</div><input type="text" id="rbaHostname" name="rbaHostname" value="${rbaHostname}" py:attrs="{'disabled': (mode == 'mirror') and 'disabled' or None}" />
          </div>
        </div>
        <div class="form-line">
          <a class="rnd_button float-right" href="javascript:button_submit(document.page_form)">Save</a>
        </div>
      </div>
      </form>
    </div>
</body>
</html>
