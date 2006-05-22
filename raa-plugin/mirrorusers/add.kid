<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import raa.templates.master ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="raa.templates.master">
<!--
    Copyright (c) 2005-2006 rPath, Inc.
    All Rights Reserved
-->
<head>
  <title>Update Mirroring Privileges</title>
  <style type="text/css">
    h5#warnText {
      color: #ff0000;
    }
  </style>

  <script type="text/javascript">
        function displayGuide(textType) {
            var user = document.getElementById('userName');
            var pass1 = document.getElementById('password1');
            var pass2 = document.getElementById('password2');
            user.readOnly = false;
            pass1.readOnly = false;
            pass2.readOnly = false;
            if (user.value == 'anonymous') {
              user.value = '';
              pass1.value = '';
              pass2.value = '';
            }
            if (textType == 'anon') {
              text = 'Creating the Anonymous User provides read-only access to the entire repository and makes its contents available to anyone with network access to this mirror.  Use caution when creating this user.';
              user.readOnly = true;
              user.value = 'anonymous';
              pass1.readOnly = true;
              pass1.value = 'anonymous';
              pass2.readOnly = true;
              pass2.value = 'anonymous';
              textStyle = 'warnText';
            }
            else if (textType == 'mirror') {
              text = 'A user with Mirroring permission can mirror and write to the repository.  Create a user of this type if you wish to mirror to this repository.';
              textStyle = 'guideText';
            }
            else if (textType = 'admin') {
              text = 'An admin user is used to access the Conary web interface directly.  A user with admin permission has the ability to create, delete, and modify other users.  The admin user can fine-tune a users\' access permissions to individual troves.  Create an admin user only if you wish to access the Conary web interface directly.  Admin privileges are not needed for mirroring.';
              textStyle = 'warnText';
            }
            var e = document.getElementsByTagName("h5");
            for (var i = 0; e.length > i; i++) {
              if (e[i].id == 'guideText') {
                var nodeId = 'guideText';
                break;
              }
              else if (e[i].id == 'warnText') {
                var nodeId = 'warnText';
                break;
              }
            }
            var oldNode = document.getElementById(nodeId);
            var newNode = document.createElement("h5");
            newNode.id = textStyle;
            var txtNode = document.createTextNode(text);
            newNode.appendChild(txtNode);
            oldNode.parentNode.replaceChild(newNode, oldNode);
        }
  </script>
</head>
<body>
  <div class="tabs">
    <ul>
      <li><a href="index"><span>Users</span></a></li>
      <li class="current"><a href="add"><span>Add User</span></a></li> 
     </ul>
  </div>
  <br/>
  <p>
   <hr />
  </p>
    <div id="add">
      <h5 py:if="error" id="warnText">${message}</h5>
      <h5 py:if="not error" id="guideText">${message}</h5>
       <form action="add" method="POST">
           <table>
                <tr>
                    <td class="label">
                        <label>User Name</label>
                    </td>
                    <td class="field">
                        <input type="text" id="userName" name="username" size="40"/>
                    </td>
                </tr>
                <tr>
                    <td class="label">
                        <label>Password</label>
                    </td>
                    <td class="field">
                        <input type="password" id="password1" name="passwd1" size="40" />
                    </td>
                </tr>
                <tr>
                    <td class="label">
                        <label>Password Again</label>
                    </td>
                    <td class="field">
                        <input type="password" id="password2" name="passwd2" size="40" />
                    </td>
                </tr>
                <tr>
                    <td class="label">
                        <label>Permission</label>
                    </td>
                    <td class="field">
                        <input  onclick="displayGuide('mirror')" checked="true" type="radio" name="perm" value="Mirror"/>Mirroring
                        <input onclick="displayGuide('anon')" type="radio" name="perm" value="Anonymous"/>Annonymous
                        <input onclick="displayGuide('admin')" type="radio" name="perm" value="Admin"/>Admin<br/>
                    </td>
                </tr>
                <tr>
                    <td colspan="2" class="buttons">
                        <button class="img" type="submit">
                          <img src="${tg.url('/static/images/apply_button.png')}" alt="Change Password" />
                        </button>
                    </td>
                </tr>
            </table>
       </form>
    </div>
</body>
</html>
<!-- vim: set ts=2 sw=2 sts=2 expandtab autoindent: -->
