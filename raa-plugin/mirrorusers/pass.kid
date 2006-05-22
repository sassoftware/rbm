<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import raa.templates.master ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="raa.templates.master">
<!--
    Copyright (c) 2005-2006 rPath, Inc.
    All Rights Reserved
-->
<head>
  <title>Update Mirroring Privileges"</title>
  <style type="text/css">
    h5#errMessage {
      color: #ff0000;
    }
  </style>
</head>
<body>
  <div class="tabs">
    <ul>
      <li><a href="index"><span>Users</span></a></li>
      <li><a href="add"><span>Add User</span></a></li> 
      <li class="current"><a href="#"><span>Change Password</span></a></li> 
     </ul>
  </div>
  <br/>
  <p>
   <hr />
  </p>
    <div id="add">
      <h5 py:if="error" id="errMessage">${message}</h5>
      <h5 py:if="not error">${message}</h5>
       <form action="changePassword" method="POST">
         <input type="hidden" name="username" value="${username}"/>
           <table>
                <tr>
                    <td class="label">
                        <label>Password</label>
                    </td>
                    <td class="field">
                        <input type="password" name="passwd1" size="40" />
                    </td>
                </tr>
                <tr>
                    <td class="label">
                        <label>Password Again</label>
                    </td>
                    <td class="field">
                        <input type="password" name="passwd2" size="40" />
                    </td>
                </tr>
                <tr>
                    <td colspan="2" class="buttons">
                        <button class="img" type="submit">
                          <img src="${tg.url('/static/images/apply_button.png')}" alt="Change Password" />
                        </button>
                        <a href="index"><button class="img" type="button">
                          <img src="${tg.url('/static/images/cancel_button.png')}" alt="Cancel" />
                        </button></a>
                    </td>
                </tr>
            </table>
       </form>
    </div>
</body>
</html>
<!-- vim: set ts=2 sw=2 sts=2 expandtab autoindent: -->
