import express from "express"
import { Client } from "pg";

const client = new Client({
    user: "postgres",
    host: "localhost",
    database: "mydb",
    password: "enter-password",
    port: 5432,
})


const server = express()
server.use(express.json())

server.get("/", async function (req, res){
    try {
        const SELECT_QUERY = "SELECT * FROM notestable"
        const result = await client.query(SELECT_QUERY)
        res.status(200).json({ success: true, notes: result.rows})
    } catch (error) {
        console.log(error.message);
        return res.status(500).json({ sucess: false, message: "Failed to save data" });
    }
})

server.post("/", async function (req, res) {

    try {
        const { title, content, price } = req.body;
        if (!title && !price){
            return res.status(404).json({ success: false, message: "Enter the Give Feilds"})
        }
        const INSERT_QUERY = "INSERT INTO notestable (title, content, price) VALUES ($1, $2, $3)";

        const result = await client.query(INSERT_QUERY, [title, content, price])
        res.status(201).json({ success: true, message: "Data Create Successfully"})
    } catch (error) {
        console.log(error.message);
        return res.status(500).json({ sucess: false, message: "Failed to save data" });
    }

});

server.put("/:id", async function (req, res) {
    try {
        const { id } = req.params
        const { title, content, price } = req.body
        const UPDATE_QUERY =  "UPDATE notestable SET title = $1, content = $2, price = $3 WHERE id = $4"
        const result = await client.query(UPDATE_QUERY, [title, content, price, id])

        if (result.rowCount === 0) {
            return res.status(404).json({ message: "Note not found" });
        }
        
        res.status(200).json({ sucess: true, message: "Note Updated Successfully"})
    } catch (error) {
        console.log(error.message);
        return res.status(500).json({ sucess: false, message: "Failed to save data" });
    }
})

server.delete("/:id", async function (req, res) {
    try {
        const { id } = req.params
        const DELETE_QUERY = "DELETE FROM notestable WHERE id = $1"
        const result = await client.query(DELETE_QUERY, [id])
        if (result.rowCount === 0) {
            return res.status(404).json({ message: "Note not found" });
        }
        
        res.status(200).json({ sucess: true, message: "Note Deleted Successfully"})
    } catch (error) {
        console.log(error.message);
        return res.status(500).json({ sucess: false, message: "Failed to save data" });
    }
})


client.connect().then( function () {
    console.log("Database Successfully Connected to Database")
    server.listen(3000)
})
