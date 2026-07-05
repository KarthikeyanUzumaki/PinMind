import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from "firebase/auth";

// Firebase web configuration keys
const firebaseConfig = {
  apiKey: "AIzaSyCLx92QU5vOIwc3DfrRA3diNGs0b_yh-jA",
  authDomain: "pinmind-df5fc.firebaseapp.com",
  projectId: "pinmind-df5fc",
  storageBucket: "pinmind-df5fc.firebasestorage.app",
  messagingSenderId: "35823225032",
  appId: "1:35823225032:web:d025f5211b026f2577bdfd",
  measurementId: "G-HBD4SVP64J"
};

// Initialize Firebase app instance
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: 'select_account' });

export const loginWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    return result.user;
  } catch (error) {
    console.error("Authentication popup failed:", error);
    throw error;
  }
};

export const logoutUser = async () => {
  try {
    await signOut(auth);
  } catch (error) {
    console.error("Sign-out request failed:", error);
    throw error;
  }
};
