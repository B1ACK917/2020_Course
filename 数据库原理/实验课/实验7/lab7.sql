use jxgl;

Create table test (id int unique AUTO_INCREMENT, rq datetime null, srq varchar (20) null, hh smallint null, mm smallint null, ss smallint null, num numeric (12,3),primary key (id))engine=MyISAM;

drop procedure ps;
DELIMITER //
CREATE PROCEDURE ps ()
begin
	set @i= 1;
	WHILE @i<= 10000 do
		INSERT INTO TEST (RQ, SRQ,HH,MM, SS,NUM)
			VALUES (NOW() ,NOW() , HOUR (NOW()),MINUTE (NOW()), SECOND (NOW()), RAND(@i) * 100);
		set @i=@i+1;
	END WHILE;
End//
DELIMITER ;

call ps;

Select @i = max(id) from test;
INSERT INTO TEST (RQ, SRQ, HH, MM, SS, NUM)
VALUES (NOW() ,NOW() , HOUR (NOW()),MINUTE (NOW()), SECOND (NOW()), RAND(@i) * 100);