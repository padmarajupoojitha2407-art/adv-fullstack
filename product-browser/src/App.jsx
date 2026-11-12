import ProductPage from "./pages/ProductPage.jsx"
import{Routes, Route, Link} from "react-router" //when adress changes, it will render the component that matches the path is routes
//link hepls to prevent to reload the page when we click on the link, it will change the address and render the component that matches the path in routes
import BrowsePage from "./pages/BrowsePage.jsx"
import ProductDetailPage from "./pages/ProductDetailPage.jsx"


function App() {
  return (
    <>
    <nav>
      <Link to ="/">All Products</Link> |<Link to ="browse"> Browse</Link>
    </nav>
    <Routes>
      <Route path="/" element={<ProductPage />} />
      <Route path="/browse" element={<BrowsePage />} />
      <Route path="/products/:id" element={<ProductDetailPage />} />
      <Route path="*" element={<h1>404 - Not Found</h1>} />
     
     
    </Routes>
    </>
  )
}

export default App