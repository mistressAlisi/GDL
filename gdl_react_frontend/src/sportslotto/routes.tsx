import { createBrowserRouter } from "react-router";
import App from "./App";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { Recovery } from "./pages/Recovery";
import { PendingTicketsPage } from "./pages/PendingTicketsPage";
import { GradedTicketsPage } from "./pages/GradedTicketsPage";
import { RootLayout } from "./components/RootLayout";
import { ProtectedRoute } from "./components/ProtectedRoute";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: RootLayout,
    children: [
      {
        index: true,
        element: (
          <ProtectedRoute>
            <App />
          </ProtectedRoute>
        ),
      },
      {
        path: "login",
        Component: Login,
      },
      {
        path: "register",
        Component: Register,
      },
      {
        path: "recovery",
        Component: Recovery,
      },
      {
        path: "tickets/pending",
        element: (
          <ProtectedRoute>
            <PendingTicketsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: "tickets/graded",
        element: (
          <ProtectedRoute>
            <GradedTicketsPage />
          </ProtectedRoute>
        ),
      },
    ],
  },
]);
