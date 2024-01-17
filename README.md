# PythonGram

<p align="center">
  <img src="logo.png" alt="PythonGram" width="256" height="256">
</p>

---

PythonGram is a REST API application implemented using the FastAPI framework.
It allows users to upload, manage, and share photos, as well as interact through comments and ratings.

---

## Table of Contents

- [Technologies](#technologies)
- [Basic functionality](#basic-functionality)
  - [Authentication](#authentication)
  - [Working with photos](#working-with-photos)
  - [Comments](#comments)
  - [Profile](#profile)
  - [Ratings](#ratings)
  - [Search](#search)
- [Usage](#usage)
- [License](#license)
- [Authors](#authors)

## Technologies

| **Module**                                                     | **Description**    |
|----------------------------------------------------------------|--------------------|
| [FastAPI](https://fastapi.tiangolo.com/)                       | Framework          |
| [Pydantic](https://pydantic-docs.helpmanual.io/)               | Validation library |
| [SQLAlchemy](https://docs.sqlalchemy.org/)                     | ORM                |
| [Alembic](https://alembic.sqlalchemy.org/en/latest/)           | Migration tool     |
| [PostgreSQL](https://www.postgresql.org/)                      | Database           |
| [Cloudinary](https://cloudinary.com/)                          | Image hosting      |
| [FastAPI-limiter](https://github.com/long2ice/fastapi-limiter) | Rate limiting      |
| [Passlib](https://passlib.readthedocs.io/en/stable/)           | Password hashing   |
| [Qrcode](https://pypi.org/project/qrcode/)                     | QR code generator  |
| [Pillow](https://pypi.org/project/Pillow/)                     | Image processing   |

## Basic functionality

### Authentication

**Endpoints:**

```HTTP
POST api/auth/signup
```
```HTTP
POST api/auth/login
```
```HTTP
POST api/auth/logout
```
```HTTP
POST api/auth/refresh_token
```

*The names speak for themselves*

The application uses JWT tokens for authentication. Users have three roles: regular user, moderator, and administrator.

To implement different access levels (regular user, moderator, and administrator),
FastAPI decorators are used to check the token and user role.

### Working with photos

**Users can perform various operations related to photos:**

- Upload photos with descriptions.
    ```HTTP
    POST api/upload_picture
    ```
- Delete photos.
    ```HTTP
    DELETE api/photos/{picture_id}
    ```
- Edit photo descriptions.
    ```HTTP
    PATCH api/photos/{picture_id}
    ```
- Retrieve a photo by a unique link.
    ```HTTP
    GET api/photos/{picture_id}
    ```
- Add up to 5 tags per photo.


- Apply basic photo transformations using [Cloudinary services](https://cloudinary.com/documentation/image_transformations).
    ```HTTP
    POST api/photos/transform
    ```
- Generate links to transformed images for viewing as URL and QR-code. Links are stored on the server.

With the help of [FastAPI decorators, described above](#authentication), administrators can perform all CRUD operations with user photos.

### Comments

**Under each photo, there is a comment section. Users can:**

- Add and read comments to each other's photos.
  ```HTTP
  POST api/comments
  ```
  ```HTTP
  GET api/comments
  ```
- Open and edit comment.
  ```HTTP
  GET api/comments/{comment_id}
  ```
  ```HTTP
  PATCH api/comments/{comment_id}
  ```
- Administrators and moderators [if you have the role](#authentication) can delete comments.
  ```HTTP
  DELETE api/comments/{comment_id}
  ```

### Profile

**Endpoints for user profile:**

- See your profile.
    ```HTTP
    GET api/users/me
    ```
- Edit your profile, or change your avatar.
    ```HTTP
    PATCH api/users/me
    ```
    ```
    PATCH api/users/avatar
    ```
- See another user's profile.
    ```HTTP
    GET api/users/{username}
    ```
- Ban users, if you have the [administrator role](#authentication).
    ```HTTP
    PATCH api/users/{username}
    ```

- Create a route for a user profile based on their unique username. It returns all user information, including name, registration date, and the number of uploaded photos.

- Users can edit their own information and view it.

- Administrators can deactivate users (ban them). Inactive users cannot log in.

### Ratings

**soon...**

### Search

**soon...**

## Usage

- [Documentation](https://pythongram.readthedocs.io/en/latest/)
- [Swagger documentation(soon)](https://pythongram.readthedocs.io/en/latest/swagger/)
- [GitHub](https://github.com/GodVov4/Basic_Name)

## License

This project is licensed under the [MIT License](LICENSE).

## Authors

- [GodVov4](https://github.com/GodVov4)
- [DSofiya](https://github.com/DSofiya)
- [fls0](https://github.com/fls0)
- [GennadiiBukh](https://github.com/GennadiiBukh)

Feel free to provide feedback, report issues, or contribute to the project!
