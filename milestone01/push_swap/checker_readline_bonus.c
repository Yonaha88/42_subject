/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   checker_readline_bonus.c                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/18 12:10:55 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/18 13:26:41 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "checker_bonus.h"

char	*get_line_checker(void)
{
	char	*line;
	char	c;
	int		i;
	int		get_char;

	line = malloc(5);
	if (!line)
		return (NULL);
	i = 0;
	get_char = 0;
	while (read(0, &c, 1) == 1)
	{
		get_char = 1;
		if (c == '\n')
			break ;
		if (i < 4)
			line[i++] = c;
	}
	if (!get_char)
	{
		free(line);
		return (NULL);
	}
	line[i] = '\0';
	return (line);
}
