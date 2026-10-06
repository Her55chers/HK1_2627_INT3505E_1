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
chạy lệnh: "curl "http://localhost:5000/books?maxPageSize=5""
Trả về:
![alt text](image.png)
Chạy lệnh: "curl "http://localhost:5000/books?status=premium&max_page_size=5"
Trả về:
![alt text](image_1.png)