create database jxgl;
use jxgl;
create table student (
	sno char(7) not null,
    sname varchar(16),
    ssex char default '男' check(ssex='男' or ssex='女'),
    sage smallint check(sage>=15 and sage<=45),
    sdept char(2),
    primary key(sno)
)engine=InnoDB;

create table course (
	cno char(2) not null,
    cname varchar(20),
    cpno char(2),
    credit smallint,
    primary key(cno),
    foreign key(cpno) references course(cno)
)engine=InnoDB;

create table sc (
	sno char(7) not null,
    cno char(2) not null,
    grade smallint null check(grade is null or (grade between 0 and 100)),
    primary key(sno,cno),
    foreign key(sno) references student(sno),
    foreign key(cno) references course(cno)
)engine=InnoDB;

insert into student values
('00001','王林','男',25,'AA'),
('00002','狗俊锋','男',31,'BB'),
('00003','狗俊锋2号','女',23,'SS'),
('00004','狗俊锋3号','男',26,'AA'),
('00005','狗俊锋4号','女',18,'BB'),
('00006','狗俊锋5号','男',35,'AA');

insert into course values
('01','上单的自我修养','01',2),
('02','中单的自我修养','01',3),
('03','打野的自我修养','01',4),
('04','辅助的自我修养','01',2),
('05','ADC的自我修养','01',4),
('06','C++从入门到入土','01',1),
('07','头发护理教程','01',2),
('08','如何成为外卖骑手','01',3);

insert into sc values
('00001','01',66),
('00001','02',78),
('00001','04',54),
('00002','02',89),
('00002','03',76),
('00002','08',54),
('00002','07',89),
('00003','06',68),
('00003','05',68),
('00003','02',78),
('00004','01',56),
('00004','02',79),
('00004','08',76),
('00005','01',56),
('00005','02',79),
('00005','04',76),
('00006','01',56),
('00006','02',79),
('00006','04',76);

use jxgl;
LOCK TABLES sc READ; #锁定表
SELECT * INTO OUTFILE 'F:/Homework/temp/sc.bak' FROM sc; #备份sc表
LOCK TABLES course READ; #锁定表
SELECT * INTO OUTFILE 'F:/Homework/temp/course.bak' FROM course; #备份course表
LOCK TABLES student READ; #锁定表
SELECT * INTO OUTFILE 'F:/Homework/temp/student.bak' FROM student; #备份student表
UNLOCK TABLES; #解锁表

SET FOREIGN_KEY_CHECKS=0; #取消外码约束，否则无法清空course表
truncate sc; # 清空sc表
truncate course; # 清空course表
truncate student; # 清空student表
SET FOREIGN_KEY_CHECKS=1; #重置外码约束

LOCK TABLES course WRITE; #锁定表
LOAD DATA INFILE 'F:/Homework/temp/course.bak' REPLACE INTO TABLE course; #恢复course表
LOCK TABLES student WRITE; #锁定表
LOAD DATA INFILE 'F:/Homework/temp/student.bak' REPLACE INTO TABLE student; #恢复student表
LOCK TABLES sc WRITE; #锁定表
LOAD DATA INFILE 'F:/Homework/temp/sc.bak' REPLACE INTO TABLE sc; #恢复sc表
UNLOCK TABLES; #解锁表