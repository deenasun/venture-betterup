"use client";

import Image from "next/image";
import { useCallback, useState, useEffect, useContext } from "react";
import { read, utils } from "xlsx";
import Table from "../components/Table.jsx";
import { DashboardContext } from "@/components/DashboardContext";

export default function Home() {
  const { courses, setCourses, getCourseByCourseID } =
    useContext(DashboardContext);

  const [loginKeys] = useState(["key1", "key2", "key3", "key4", "key5"]);
  const [inputKey, setInputKey] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showDownloadAndVisualize, setShowDownloadAndVisualize] =
    useState(false); // New state for button visibility

  const checkExtension = useCallback((file) => {
    const extension = file.name.split(".").pop();
    return extension;
  }, []);

  useEffect(() => {
    console.log("WOOHOO:", courses);
  }, [courses]);

  function handleFileSelect(target) {
    if (!target?.files?.length || target?.files?.length == 0) {
      return;
    }
    const file = target.files[0];
    const extension = checkExtension(file);

    if (extension == "csv") {
      loadCSVFile(file);
    } else if (extension == "xlsx") {
      loadXLSXFIle(file);
    } else {
      console.log(
        "File type not supported! File must be of type .csv or .xlsx"
      );
    }
  }

  const loadCSVFile = useCallback((file) => {
    const reader = new FileReader();
    reader.readAsText(file);
    reader.onload = (event) => {
      const fileContent = reader.result;
      const wb = read(fileContent, { type: "string" });
      const entries = utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]]);
      setCourses(entries);
    };
  }, []);

  const loadXLSXFIle = useCallback((file) => {
    const reader = new FileReader();
    reader.readAsArrayBuffer(file);
    reader.onload = () => {
      const fileContent = reader.result;
      const workbook = read(fileContent, {
        type: "binary",
      });

      const entries = utils.sheet_to_json(
        workbook.Sheets[workbook.SheetNames[0]]
      );
      setCourses(entries);
    };
  }, []);

  const handleLogin = () => {
    if (loginKeys.includes(inputKey)) {
      setIsLoggedIn(true); // Set login status to true
    } else {
      alert("Invalid login key!"); // Alert for invalid key
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center">
          <h1 className="text-3xl">
            Welcome to the Doceobo Course Analysis System
          </h1>
          <h2 className="mb-4 text-xl font-bold">Login to Access</h2>
          <input
            type="password"
            value={inputKey}
            onChange={(e) => setInputKey(e.target.value)}
            placeholder="Enter login key"
            className="border border-gray-300 rounded p-2 mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleLogin}
            className="bg-blue-500 text-white rounded p-2 hover:bg-blue-600 transition duration-200"
          >
            Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <h1 className="text-3xl">
          Welcome to the Doceobo Course Analysis System
        </h1>
        <h2 className="mb-4 text-xl font-bold">Choose an option:</h2>

        {/* Centered file input */}
        <div className="flex justify-center">
          <input
            type="file"
            id="fileInput"
            onChange={(event) => {
              handleFileSelect(event.target);
            }}
          />
        </div>

        {/* Centered buttons container */}
        <div className="flex flex-col items-center justify-center">
          {/* Option to scrape BetterUp */}
          <button
            onClick={() => {
              console.log("Scrape BetterUp button clicked");
              setShowDownloadAndVisualize(true); // Show the new buttons when clicked
            }}
            className="bg-blue-500 text-white rounded p-2 hover:bg-blue-600 transition duration-200"
          >
            Scrape BetterUp
          </button>

          {/* Conditionally render the Download Data and Visualize Data buttons */}
          {showDownloadAndVisualize && (
            <div className="flex flex-col items-center justify-center">
              <button
                onClick={() => {
                  console.log("Download Data button clicked");
                }}
                className="bg-white text-black rounded p-2 mb-12 hover:bg-gray-200 transition duration-200 w-full" // Changed to white background and black text, added mb-12 for padding
              >
                Download Data
              </button>

              <button
                onClick={() => {
                  console.log("Visualize Data button clicked");
                }}
                className="bg-white text-black rounded p-2 hover:bg-gray-200 transition duration-200 w-full" // Changed to white background and black text
              >
                Visualize Data
              </button>
            </div>
          )}
        </div>

        {courses && <Table />}
      </main>
    </div>
  );
}
