import OpenAI from 'openai';
import fs from 'fs';
import dotenv from "dotenv";

// Load environment variables from the .env file
dotenv.config();

export class OpenAIService {
    private openai: OpenAI;

    constructor() {
        this.openai = new OpenAI({
            apiKey: process.env.OPENAI_API_KEY as string
        });
    }

    async generateImageDescription(imagePath: string): Promise<string> {
        try {
            // Read image file as base64
            const imageBuffer = await fs.promises.readFile(imagePath);
            const base64Image = imageBuffer.toString('base64');

            const response = await this.openai.chat.completions.create({
                model: "gpt-4o-mini",
                messages: [
                    {
                        role: "user",
                        content: [
                            {
                                type: "text",
                                text: "Please provide a detailed description of this image. Focus on the main subjects, activities, setting, and notable details. Keep the description natural and concise."
                            },
                            {
                                type: "image_url",
                                image_url: {
                                    url: `data:image/jpeg;base64,${base64Image}`
                                }
                            }
                        ],
                    },
                ],
                max_tokens: 150
            });

            return response.choices[0]?.message?.content || 'No description available';
        } catch (error) {
            console.error('Error generating image description:', error);
            throw new Error('Failed to generate image description');
        }
    }
}