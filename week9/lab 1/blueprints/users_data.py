users_data = {
    1: {
        "first_name": "An",
        "last_name": "Nguyen",
        "full_name": "Nguyen Van An",
        "email": "an.nguyen@example.com",
    },
    2: {
        "first_name": "Binh",
        "last_name": "Tran",
        "full_name": "Tran Thi Binh",
        "email": "binh.tran@example.com",
    },
    3: {
        "first_name": "Cuong",
        "last_name": "Le",
        "full_name": "Le Minh Cuong",
        "email": "cuong.le@example.com",
    },
}


def create_user(first_name, last_name, email):
    """Thêm user mới (dùng cho POST v2). full_name được suy ra để v1 vẫn đọc được."""
    uid = max(users_data, default=0) + 1
    users_data[uid] = {
        "first_name": first_name,
        "last_name": last_name,
        "full_name": f"{last_name} {first_name}",
        "email": email,
    }
    return uid