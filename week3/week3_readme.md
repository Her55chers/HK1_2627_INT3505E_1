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
StatusCode        : 200
StatusDescription : OK
Content           : {
                      "customers": [
                        {
                          "email": "customer{1}@example.com",
                          "id": "customer_1",
                          "name": "customer_{i}"
                        }
                      ],
                      "next_page_token": "eyJpZCI6ICJjdXN0b21lcl8xIn0="
                    }
                    
RawContent        : HTTP/1.1 200 OK
                    Connection: close
                    Content-Length: 187
                    Content-Type: application/json
                    Date: Tue, 06 Oct 2026 10:31:49 GMT
                    Server: Werkzeug/3.1.8 Python/3.14.7
                    
                    {
                      "customers": [
                        {
                          "em...
Forms             : {}
Headers           : {[Connection, close], [Content-Length, 187], [Content-Type, 
                    application/json], [Date, Tue, 06 Oct 2026 10:31:49 GMT]...}
Images            : {}
InputFields       : {}
Links             : {}
ParsedHtml        : System.__ComObject
RawContentLength  : 187