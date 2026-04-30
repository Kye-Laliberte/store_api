const BASE_URL = "http://localhost:8000";
const ITEMS_URL = `${BASE_URL}/items`;
//from fastapi.middleware.cors import CORSMiddleware
// Function to fetch items from the backend
export async function getItem(Item_id) {
    /**fetches a item */
    try{
        const response = await fetch(`${ITEMS_URL}/${Item_id}/details`, {
            method: 'GET',
            headers: {'Content-Type': 'application/json'}
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);}

        const data = await response.json();
        return data;

    } catch (error) {
        console.error("Error fetching item:", error);
        throw error;
    }
}

export async function getAllItems() {
    try{
        const response = await fetch(`${ITEMS_URL}/get_all`, {
            method: 'GET',
            headers: {'Content-Type': 'application/json'}
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching all items:", error);
        throw error;
    }
}