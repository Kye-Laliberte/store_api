import { useEffect } from "react";
import api from "/src/api/axios";


//from fastapi.middleware.cors import CORSMiddleware
// Function to fetch items from the backend
export async function getItem(Item_id) {
    /**fetches a item */
    try{
        const response = await api.get(`/items/${Item_id}/details`);
        
        return response.data;
    } catch (error) {
        console.error("Error fetching item:", error);
        throw error;
    }
}

export async function getAllItems() {
    try{
        const response = await api.get(`/items/get_all`);

        return response.data;
    } 
    catch (error) {
        console.error("Error fetching all items:", error);
        throw error;
    }
  }        
