use shop;

create table book(
	book_id int not null auto_increment,
    book_name char(64),
    num int,
    price int,
    primary key(book_id)
)ENGINE = InnoDB AUTO_INCREMENT = 1;

create table supplier(
	sup_id int not null auto_increment,
    sup_book_id int,
    sup_price int,
    primary key(sup_id)
)ENGINE = InnoDB;

create table trade(
	trade_id int not null auto_increment,
    book_id int,
    trade_type enum('in','out','buy'),
    trade_num int,
    primary key(trade_id)
)ENGINE = InnoDB;

insert into book(book_name,num,price) values
('线性代数及其应用',3,30),
('离散数学及其应用',4,23),
('大学学术英语',6,45),
('大学物理',4,35);

insert into book(book_name,num,price) values
('计算机组成原理',5,33650);


insert into supplier(sup_book_id,sup_price) values
(1,23000),
(2,15350),
(1,26500),
(3,23500),
(3,56600),
(4,36400),
(2,28350);

select * from book where book_id=1 or book_name='test2';
insert into trade(book_id,trade_type) value(1,'in');
select* from trade;

update book set num=num-1 where book_id=1;

select * from book;
select * from supplier;

drop database if exists shop;