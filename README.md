# PythonGram

<p align="center">
  <img src="logo.svg" alt="PythonGram" width="256" height="256">
</p>

PythonGram is a REST API application implemented using the FastAPI framework. It allows users to upload, manage, and share photos, as well as interact through comments and ratings.

## Table of Contents

- [Authentication](#authentication)

- [Working with Photos](#working-with-photos)

- [Comments](#comments)

- [Additional Features](#additional-features)

- [Deployment](#deployment)

- [Testing](#testing)

- [Contributing](#contributing)

- [License](#license)

- [Authors](#authors)

## Authentication

The application uses JWT tokens for authentication. Users have three roles: regular user, moderator, and administrator. The first user in the system is always an administrator.

To implement different access levels (regular user, moderator, and administrator), FastAPI decorators are used to check the token and user role.

## Working with Photos

Users can perform various operations related to photos:

- Upload photos with descriptions.

- Delete photos.

- Edit photo descriptions.

- Retrieve a photo by a unique link.

- Add up to 5 tags per photo. Adding a tag is optional when uploading a photo.

- Apply basic photo transformations using Cloudinary services (https://cloudinary.com/documentation/image_transformations).

- Generate links to transformed images for viewing as URL and QR-code. Links are stored on the server.

Administrators can perform all CRUD operations with user photos.

## Comments

Under each photo, there is a comment section. Users can:

- Add comments to each other's photos.

- Edit their own comments (no deletion allowed).

- Administrators and moderators can delete comments.

- Save creation and update times for comments in the database.

## Additional Features

- Create a route for a user profile based on their unique username. It returns all user information, including name, registration date, and the number of uploaded photos.

- Users can edit their own information and view it.

- Administrators can deactivate users (ban them). Inactive users cannot log in.

## Deployment

1\. Clone the repository:

```bash

git clone https://github.com/your-username/your-project.git

cd your-project

```

2\. Install dependencies:

```bash

pip install -r requirements.txt

```

3\. Set up a PostgreSQL database for user, photo, and comment storage.

4\. Configure the database connection in the application.

5\. Run the FastAPI application:

```bash

uvicorn main:app --reload

```

## Testing

Ensure the application has comprehensive test coverage, aiming for more than 90%.

## Contributing

1\. Fork the repository.

2\. Create a new branch for your feature or bugfix: `git checkout -b feature/your-feature`.

3\. Commit your changes: `git commit -m "Add your feature"`.

4\. Push your branch: `git push origin feature/your-feature`.

5\. Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Authors

- [GodVov4](https://github.com/GodVov4)
- [DSofiya](https://github.com/DSofiya)
- [fls0](https://github.com/fls0)
- [GennadiiBukh](https://github.com/GennadiiBukh)

Feel free to provide feedback, report issues, or contribute to the project!