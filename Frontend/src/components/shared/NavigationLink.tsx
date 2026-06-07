import { Link } from "react-router-dom";

type Props = {
  to: string;
  bg: string;
  text: string;
  textcolor: string;
  onClick?: () => Promise<void>;
};

const NavigationLink = ({ to, bg, text, textcolor, onClick }: Props) => {
  return (
    <Link
      className="navLink"
      to={to}
      onClick={onClick} // Only attach if provided
      style={{
        background: bg,
        color: textcolor, // Fixed text color issue
        padding: "10px 20px",
        borderRadius: "8px",
        textDecoration: "none",
        fontWeight: "bold",
        transition: "0.3s",
        margin: "5px",
        display: "inline-block", // Ensures proper spacing
      }}
      onMouseOver={(e) => (e.currentTarget.style.opacity = "0.8")}
      onMouseOut={(e) => (e.currentTarget.style.opacity = "1")}
    >
      {text}
    </Link>
  );
};

export default NavigationLink;
