-- use jxgl;
-- create user RONALDO identified by 'NIKE';
-- rename user RONALDO to TEACHER;
-- set password for TEACHER='hello';
-- drop user TEACHER;

-- create user Chrisl@'%' identified by '1234';
-- create user Chris2@'%' identified by '12345';
-- create user Chris3@'%.com' identified by '123456';

grant create,update on jxgl.student to Chris1@'%' with GRANT option;

grant create on jxgl.* to Chris3@'%.com';

REVOKE all on jxgl.* FROM Chrisl@'%';


select* from MYSQL.user;