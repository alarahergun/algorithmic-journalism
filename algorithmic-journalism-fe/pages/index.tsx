import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { DataGrid, GridToolbar } from "@mui/x-data-grid";
import { GetServerSideProps } from "next";
import clientPromise from "../lib/mongodb";

interface News {
  _id: string;
  title: string;
  summary: string;
  url: string;
  date: Date;
}

interface NewsProps {
  movies: News[];
}

const Movies: React.FC<NewsProps> = ({ news }) => {
  const columns: any = [
    { field: "_id", headerName: "ID", width: 90, align: "center" },
    { field: "title", headerName: "Title", width: 400, align: "center" },
    { field: "summary", headerName: "Summary", width: 400, align: "center" },
    {
      field: "url",
      headerName: "URL",
      width: 400,
      type: "url",
      align: "center",
      renderCell: (params: any) => {
        const openUrlInNewTab = () => {
          window.open(params.value, "_blank");
        };

        return (
          <div style={{ cursor: "pointer" }} onClick={openUrlInNewTab}>
            {params.value}
          </div>
        );
      },
    },
    { field: "date", headerName: "Fetch Date", width: 400, align: "center" },
  ];

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        height: "100vh",
        px: 3,
        py: 3,
        backgroundColor: "#f5f5f5",
      }}
    >
      <Typography
        variant="h3"
        sx={{
          mb: 2,
        }}
      >
        Daily News
      </Typography>
      <Box
        sx={{
          display: "inline-flex",
          flexDirection: "column",
          //backgroundColor: "#fafafa",
        }}
      >
        <DataGrid
          rows={news}
          columns={columns}
          getRowHeight={() => "auto"}
          initialState={{
            pagination: {
              paginationModel: {
                pageSize: 5,
              },
            },
          }}
          slots={{ toolbar: GridToolbar }}
          pageSizeOptions={[5]}
          checkboxSelection
          disableRowSelectionOnClick
        />
      </Box>
    </Box>
  );
};

export default Movies;

export const getServerSideProps: GetServerSideProps = async () => {
  try {
    const client = await clientPromise;
    const db = client.db("news");
    const news = await db.collection("news").find({}).toArray();

    news.forEach((obj) => {
      obj.id = obj._id;
    });

    return {
      props: { news: JSON.parse(JSON.stringify(news)) },
    };
  } catch (e) {
    console.error(e);
    return { props: { news: [] } };
  }
};
