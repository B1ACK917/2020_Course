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

-- select sno,sname
-- from student
-- where ssex = '男' and sage > 23;

-- select distinct student.sno,sname
-- from student,sc
-- where student.sno = sc.sno and ssex = '女' ;

-- select course.cno
-- from course
-- where course.cno not in (
-- 	select sc.cno
-- 	from student,sc
-- 	where student.sno = sc.sno
-- 	and student.sname = '王林'
-- );

-- select student.sno
-- from student,sc
-- where student.sno = sc.sno
-- group by sc.sno
-- having count(*) >= 2 ;

-- select course.cno,cname
-- from course,sc
-- where course.cno = sc.cno
-- group by sc.cno
-- having count(*)=
-- 	(
-- 	select count(*)
-- 	from student
-- 	);

-- select avg(grade)
-- 	from course join sc using(cno)
-- 	where sno in (
-- 		select distinct sno
-- 			from course join sc using(cno)
-- 			where credit=3
-- 			group by sno
-- 			having count(cno)=(
-- 				select count(cno) 
-- 					from course
-- 					where credit=3
-- 				)
-- 			)
-- 	group by sno;

-- select count(*) 
-- from course 
-- where course.cno 
-- in 
-- 	( 
-- 	select sc.cno 
-- 	from sc 
-- 	);

-- select avg(sage)
-- from student,sc
-- where student.sno = sc.sno and sc.cno = '04' ;

-- select cname,avg( grade )
-- from course,sc
-- where credit = 3 and course.cno = sc.cno
-- group by cname;

-- select cno,count(cno)
-- from sc
-- group by cno
-- having count(cno) > 3
-- order by count(cno) desc,cno asc;

select X.sname
from student as X,student as Y
where 
Y.sname='王林'and X.sno>Y.sno and X.sage<Y.sage;
