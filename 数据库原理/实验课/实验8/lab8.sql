-- create database jxgl;
use jxgl;
-- create table student (
-- 	sno char(7) not null,
--     sname varchar(16),
--     ssex char default '男' check(ssex='男' or ssex='女'),
--     sage smallint check(sage>=15 and sage<=45),
--     sdept char(2),
--     primary key(sno)
-- )engine=InnoDB;

-- insert into student values
-- ('00002','狗俊锋','男',31,'BB'),
-- ('00003','狗俊锋2号','女',23,'SS'),
-- ('00004','狗俊锋3号','男',26,'AA'),
-- ('00005','狗俊锋4号','女',18,'BB'),
-- ('00006','狗俊锋5号','男',35,'AA'),
-- ('00007','狗俊锋6号','女',23,'SS'),
-- ('00008','狗俊锋7号','男',26,'AA'),
-- ('00009','狗俊锋8号','女',18,'BB'),
-- ('00010','狗俊锋9号','男',35,'AA'),
-- ('00011','狗俊锋10号','女',23,'SS'),
-- ('00012','狗俊锋11号','男',26,'AA'),
-- ('00013','狗俊锋12号','女',18,'BB'),
-- ('00014','狗俊锋13号','男',35,'AA');


-- (2)

-- delimiter //
-- create procedure select_s()
-- begin
--     select *
--     from student
--     where ssex='女';
-- end//
-- delimiter ;

-- call select_s();

-- (3)

-- delimiter //
-- create procedure insrectos(_sno char(7))
-- begin
--     select sname,sage
--     from student
--     where sno=_sno;
-- end//
-- delimiter ;

-- call insrectos('00005');

-- (4)

update jxgl.Stored_Procedures
set name='SELECT_STUDENT',
specific_name='SELECT_STUDENT'
where name='select_s';