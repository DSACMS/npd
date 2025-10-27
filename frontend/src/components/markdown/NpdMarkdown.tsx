import Markdown from "react-markdown"
import { MdComponents } from "./MdComponents"

export const NpdMarkdown = ({ content }: { content: string }) => {
  return <Markdown components={MdComponents}>{content}</Markdown>
}
