import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";

// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  exmaple: "example",
};

const app = initializeApp(firebaseConfig);
export const database = getDatabase(app);