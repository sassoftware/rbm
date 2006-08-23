<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import raa.templates.master ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="raa.templates.master">
<!--
    Copyright (c) 2005-2006 rPath, Inc.
    All Rights Reserved
-->
<head>
  <title>Manage Repository Users</title>
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
              var text = 'Anonymous -- Creating a user with anonymous permission makes the contents of your rBuilder Mirror repository available -- on a read-only basis -- to anyone with network access.';
              var warningText = 'Caution: Creating an anonymous user bypasses all username and entitlement-based authentication!';
              user.readOnly = true;
              user.value = 'anonymous';
              pass1.readOnly = true;
              pass1.value = 'anonymous';
              pass2.readOnly = true;
              pass2.value = 'anonymous';
            }
            else if (textType == 'mirror') {
              text = 'Mirroring -- Creating a user with mirroring permission allows the user to mirror the contents of an rBuilder Appliance to this repository, or to mirror the contents of this repository to another repository.';
              warningText = '';
            }
            else if (textType = 'admin') {
              var text = 'Admin Access -- Creating a user with admin permission makes it possible to perform low-level operations on your rBuilder Mirror repository.  A user with admin permission has the ability to create, delete, and modify other users, and fine-tune access permissions across the repository.';
              var warningText = 'Caution: Admin users have the ability to disrupt the operation of your rBuilder Mirror repository.  Create an admin user only if you have a specific need to do so!';
            }
            var oldNode = document.getElementById('guideText');
            var newNode = document.createElement("h5");
            var txtNode = document.createTextNode(text);
            newNode.id = 'guideText';
            newNode.appendChild(txtNode);
            oldNode.parentNode.replaceChild(newNode, oldNode);
            var oldWNode = document.getElementById('warnText');
            var newWNode = document.createElement("h5");
            newWNode.id = 'warnText';
            var txtWNode = document.createTextNode(warningText);
            newWNode.appendChild(txtWNode);
            oldWNode.parentNode.replaceChild(newWNode, oldWNode);
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
      <h5 id="guideText">${message}</h5>
      <h5 id="warnText"></h5>
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
                        <input  onclick="displayGuide('mirror')" checked="true" type="radio" name="perm" style="width: auto;" value="Mirror"/>Mirroring
                        <input onclick="displayGuide('anon')" type="radio" name="perm" value="Anonymous" style="width: auto;"/>Anonymous
                        <input onclick="displayGuide('admin')" type="radio" name="perm" value="Admin" style="width: auto;"/>Admin<br/>
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
