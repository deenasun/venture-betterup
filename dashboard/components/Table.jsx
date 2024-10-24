import { useContext } from "react"
import { DashboardContext } from "./DashboardContext"
import Row from "./Row"

export default function Table() {

    const {courses} = useContext(DashboardContext)

    console.log('TABLE',courses)

    if (!courses) {
        return <div>Loading...</div>
    }

    return (
        <div>
            {
        courses.map((course) => {
            return (<Row key={course['Course ID']} courseId={course['Course ID']} />)
        })}
        </div>
    )
}