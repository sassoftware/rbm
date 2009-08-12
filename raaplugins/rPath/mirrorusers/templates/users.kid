<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import raa.templates.master ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="raa.templates.master">
<!--
    Copyright (c) 2005-2006 rPath, Inc.
    All Rights Reserved
-->

<?python
from raa.templates.tabbedpagewidget import TabbedPageWidget
from rPath.mirrorusers import pageList, orderList
from raa.web import getConfigValue
?>

<head>
  <title>${getConfigValue('product.productName')}: Manage Repository Users</title>
    <script type="text/javascript">
    <![CDATA[
        function deleteUser(username) {
            d = postRequest('deleteUser', Array('username'), Array(username), callbackMessage, callbackErrorGeneric, false);
            d = d.addCallback(reloadNoHistory);
            return d;
        }    
        function promptDelete(username) {
            var messageBox = new ModalMessageBox(["Do you really want to delete the user " + username + " from the repository?"],
                                 "Delete User", [["Yes", null, function() { deleteUser(username); } ], ["No"]]);
            messageBox.show();
        }
                                             
        function passChange(username) {
            pct = document.getElementById('passChangeText');
            pct.innerHTML = "Changing password for " + username + ":";
            userName = document.getElementById('username');
            userName.value = username;
            pc = document.getElementById('passwordChange');
            pc.style.display = 'block';
        }    

        function clearPassChangeFields() {
            forEach(['oldpwd', 'pwd1', 'pwd2', 'currentpw'],
                            function (x) { if ($(x) != null) $(x).value=''; });
        }

        function passChangeSub(form) {
            d = postFormData(form, 'changePassword', callbackMessage, callbackErrorGeneric, false);
            d.addCallback(function () { clearPassChangeFields(); pc = document.getElementById('passwordChange'); pc.style.display = 'none'; });
        }   
    ]]>
    </script>
</head>
<body>
  <div class="page-content">
    ${TabbedPageWidget(value=pageList, orderList=orderList)}
    <div id="users" py:if="userData">
    Repository users provide access to various aspects of Update Service, including mirroring, anonymous, and administrative access.  Click on the "Add User" tab to create a new repository user, or use the "Delete" or "Password" links below to delete a user or change their password.
    <form>
    <table class="list" cellspacing="0">
    <thead>
      <tr>
         <th align="left">User</th>
         <th align="left" id="logItemHeading">Permission</th>
         <th align="left" id="logItemHeading">Options</th>
      </tr>
    </thead>
    <tbody style="height : auto; overflow: auto; padding-right: 2em; ">
      <tr py:for="x in userData" py:attrs="{'class': x[2]}" >
         <td valign="top" align="center" id="logItem" width="130">${x[0]}</td>
         <td valign="top" align="center" id="logItem">${x[1]}</td>
         <td valign="top" align="center" id="logItem"><a href="javascript:void(0);" onclick="javascript:promptDelete('${x[0]}');">Delete</a> | <a href="javascript:void(0);" onclick="javascript:passChange('${x[0]}');">Change Password</a></td>
      </tr>
    </tbody>
    </table>
    </form>
    <br /><br />
    <form id="passChangeForm" name="passChangeForm" onsubmit="javascript:passChangeSub(this);">
    <div class="page-section-content" id="passwordChange" name="passwordChange" style="display: none">
      <div name="passChangeText" id="passChangeText"></div>
      <input type="hidden" name="username" id="username" value="" />
      <div class="form-line">
        <label for="currentpw" class="pwd-label-div">Admin password: </label>
        <input type="password" id="currentpw" name="currentpw" />
      </div>
      <div class='form-line'>
        <label for="pwd1" class="pwd-label-div">New password: </label>
        <input type="password" id="pwd1" name="pwd1" />
      </div>
      <div class="form-line">
        <label for="pwd2" class="pwd-label-div">Confirm new password: </label>
        <input type="password" id="pwd2" name="pwd2" />
      </div>
      <a class="rnd_button float-right" id="Change" href="javascript:void(0);" onclick="javascript:button_submit(document.passChangeForm)">Change</a>
    </div>
    </form>
    </div>
    <div py:if="not userData"><p>Repository users provide access to various aspects of Update Service, including mirroring, anonymous, and administrative operations.  Click on the "Add User" tab to create a repository user.</p><p>There are currently no repository users.</p></div>
  </div>
</body>
</html>
<!-- vim: set ts=2 sw=2 sts=2 expandtab autoindent: -->
