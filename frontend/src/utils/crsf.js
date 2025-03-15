export async function getCSRFToken() {
    try {
        const response = await fetch("http://127.0.0.1:8000/csrf/", {
            credentials: "include", // Allows cookies to be sent with the request
        });

        if (!response.ok) {
            throw new Error("Failed to fetch CSRF token");
        }

        const data = await response.json();
        return data.csrfToken;
    } catch (error) {
        console.error("Error fetching CSRF token:", error);
        return null;
    }
}
