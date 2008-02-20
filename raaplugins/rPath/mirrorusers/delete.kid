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
    h5#warn {
      color: #ff0000;
    }
  </style>
</head>
<body>
  <div class="tabs">
    <ul>
      <li><a href="index"><span>Users</span></a></li>
      <li><a href="add"><span>Add User</span></a></li> 
      <li class="current"><a href="#"><span>Delete User</span></a></li> 
     </ul>
  </div>
  <br/>
  <p>
   <hr />
  </p>
    <div id="del">
      <h3>Confirm:</h3>
      <h5 id="warn">Delete the repository user "${username}"?</h5>
       <form action="deleteUser" method="POST">
         <input type="hidden" name="username" value="${username}"/>
         <input type="hidden" name="confirm" value="True"/>
         <input class="button" type="submit" value="Delete User"/>
       </form>

       <input class="button" type="submit" onclick="javascript: window.location.replace('index'); return false;" value="Cancel"/>
    </div>
</body>
</html>
<!-- vim: set ts=2 sw=2 sts=2 expandtab autoindent: -->
