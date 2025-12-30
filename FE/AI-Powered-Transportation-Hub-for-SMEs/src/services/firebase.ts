import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";

// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBpIK5ncV0xQwcIMWJKk1wK1EhH6OL7Gb4",
  authDomain: "cuoiki-34b92.firebaseapp.com",
  databaseURL: "https://cuoiki-34b92-default-rtdb.firebaseio.com",
  projectId: "cuoiki-34b92",
  storageBucket: "cuoiki-34b92.firebasestorage.app",
  messagingSenderId: "242982922424",
  appId: "1:242982922424:web:a6787dc2e13c15a46aac4d",
  measurementId: "G-M96MY55FW9"
};

const app = initializeApp(firebaseConfig);
export const database = getDatabase(app);