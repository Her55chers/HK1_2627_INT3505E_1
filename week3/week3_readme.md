*** LAB 1
1. Các resourses: Users, posts, comments, tags, follow(quan hệ).
2. Phân loại:
Collection: /users, /posts, /tags
Item: /users/{id}, /posts/{id}, /tags/{id}, /comments/{id}
Sub-resource: /posts{id}/comments, /posts/{id}tags, /users/{id}/posts, users/{id}/followers, /users/{id}/following
3.Sơ đồ cây:
/api/v1
├── /users
│   ├── GET, POST                         
│   └── /{user_id}
│       ├── GET, PATCH, DELETE            
│       ├── /posts          GET           
│       ├── /followers      GET          
│       └── /following      GET          
│           └── /{target_id}  PUT, DELETE 
├── /posts
│   ├── GET, POST                        
│   └── /{post_id}
│       ├── GET, PATCH, DELETE
│       ├── /comments
│       │   ├── GET, POST
│       │   └── /{comment_id}  GET, PATCH, DELETE
│       └── /tags
│           ├── GET
│           └── /{tag_id}  PUT, DELETE    
└── /tags
    ├── GET, POST
    └── /{tag_id}  GET
*** LAB 3
Sau khi chạy week3_lab3.py
** Cài đặt Cursors
chạy lệnh: "curl "http://localhost:5000/books?maxPageSize=5"" 
Trả về:
![alt text](/resources/image.png)
** Cài đặt Filter
Chạy lệnh: "curl "http://localhost:5000/books?status=premium&max_page_size=5"
Trả về:
![alt text](/resources/image_1.png)
** Cài đặt Sort
Chạy lệnh "curl "http://localhost:5000/books?status=premium&max_page_size=5&sort_by=name" "
Và "curl "http://localhost:5000/books?status=premium&max_page_size=5&sort_by=name&page_token=<token>" "
Trả về: 
![alt text](/resources/image_2.png)
![alt text](/resources/image_3.png)
** Cài đặt sparse fields
Chạy lệnh : "curl "http://localhost:5000/books?fields=id,name&max_page_size=3" "
Trả về: 
![alt text](/resources/image_4.png)