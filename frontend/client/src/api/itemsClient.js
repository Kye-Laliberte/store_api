import api from "./axios";


//from fastapi.middleware.cors import CORSMiddleware
// Function to fetch items from the backend
export async function getItem(Item_id) {
    /**fetches a item */
    try{
        const response = await api.get(`/items/${Item_id}/details`, {
            Item_id: Item_id
        });
        
        return response.data;
    } catch (error) {
        console.error("Error fetching item:", error);
        throw error;
    }
}

export async function getAllItems() {
    try{
        const response = await api.get(`items/get_all`);
        

        return response.data;
    } 
    catch (error) {
        console.error("Error fetching all items:", error);
        throw error;
    }
}
        